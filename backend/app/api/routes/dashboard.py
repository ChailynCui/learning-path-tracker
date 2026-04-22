import random
from datetime import date, datetime, time, timedelta

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.entities import LearningPath, LearningUnit, UserStats
from app.schemas.dashboard import (
    DashboardResponse,
    ReviewItem,
    RouteCard,
    TodayTask,
    WeeklyGoal,
    WeeklyGoalUpdateRequest,
)
from app.services.gamification import MOTIVATIONS

router = APIRouter()


def _current_week_start(today: date) -> date:
    return today - timedelta(days=today.weekday())


def _daily_target_count(path: LearningPath) -> int:
    if path.rule_type == "range" and path.range_start and path.range_end:
        return max(path.range_end - path.range_start + 1, 1)
    if path.rule_type == "interval":
        return 1
    return max(path.daily_chapter_count or 1, 1)


def _default_plan_days(path: LearningPath) -> int:
    if path.rule_type == "interval":
        return max(path.interval_days or 1, 1)
    return 1


def _has_custom_plan(path: LearningPath) -> bool:
    default_plan = _default_plan_days(path)
    return any(max(unit.planned_days or 1, 1) != default_plan for unit in path.units)


def _expected_done_by_custom_plan(path: LearningPath, elapsed_days: int) -> int:
    expected = 0
    consumed = 0
    for unit in path.units:
        consumed += max(unit.planned_days or 1, 1)
        if consumed <= elapsed_days:
            expected += 1
        else:
            break
    return expected


def _today_units_for_path(path: LearningPath) -> list[LearningUnit]:
    pending = [unit for unit in path.units if unit.status != "done"]
    if not pending:
        return []

    if _has_custom_plan(path):
        return [pending[0]]

    if path.rule_type == "interval":
        if not path.start_date:
            return [pending[0]]
        elapsed_days = max((date.today() - path.start_date).days, 0)
        interval_days = max(path.interval_days or 1, 1)
        if elapsed_days % interval_days == 0:
            return [pending[0]]
        return []

    if path.rule_type == "range" and path.range_start and path.range_end:
        scoped = [
            unit
            for unit in pending
            if path.range_start <= unit.unit_order <= path.range_end
        ]
        if scoped:
            return scoped

    return pending[: _daily_target_count(path)]


def _build_weekly_goal(db: Session, stats: UserStats, ongoing_paths: list[LearningPath]) -> WeeklyGoal:
    today = date.today()
    week_start = _current_week_start(today)
    if stats.week_goal_start != week_start:
        stats.week_goal_start = week_start
    if stats.week_goal_target < 1:
        stats.week_goal_target = 5

    week_start_dt = datetime.combine(week_start, time.min)
    completed = (
        db.query(LearningUnit)
        .filter(LearningUnit.completed_at.is_not(None), LearningUnit.completed_at >= week_start_dt)
        .count()
    )
    progress = round(min(completed / stats.week_goal_target * 100, 100), 2)

    overdue_units = 0
    overdue_titles: list[str] = []
    for path in ongoing_paths:
        if not path.start_date:
            continue
        elapsed_days = max((today - path.start_date).days + 1, 0)
        if _has_custom_plan(path):
            expected_done = min(_expected_done_by_custom_plan(path, elapsed_days), path.total_units)
        elif path.rule_type == "interval":
            interval_days = max(path.interval_days or 1, 1)
            expected_done = min(((elapsed_days - 1) // interval_days) + 1, path.total_units)
        else:
            expected_done = min(elapsed_days * _daily_target_count(path), path.total_units)
        overdue = max(expected_done - path.completed_units, 0)
        if overdue <= 0:
            continue
        overdue_units += overdue
        pending_titles = [unit.unit_title for unit in path.units if unit.status != "done"][:overdue]
        overdue_titles.extend([f"{path.title} · {title}" for title in pending_titles])

    return WeeklyGoal(
        target=stats.week_goal_target,
        week_start=stats.week_goal_start or week_start,
        completed=completed,
        progress=progress,
        overdue_units=overdue_units,
        overdue_titles=overdue_titles[:12],
    )


@router.get("", response_model=DashboardResponse)
def get_dashboard(db: Session = Depends(get_db)):
    stats = db.get(UserStats, 1)
    paths = db.query(LearningPath).order_by(LearningPath.created_at.desc()).all()
    ongoing = [path for path in paths if path.status == "ongoing"]
    completed = [path for path in paths if path.status == "completed"]

    today_task = TodayTask()
    for path in ongoing:
        today_units = _today_units_for_path(path)
        if today_units:
            first = today_units[0]
            last = today_units[-1]
            title = first.unit_title
            unit_id = first.id
            if len(today_units) > 1:
                title = f"{first.unit_title} ~ {last.unit_title}"
                unit_id = None
            today_task = TodayTask(
                path_id=path.id,
                path_title=path.title,
                unit_id=unit_id,
                unit_title=title,
                unit_ids=[unit.id for unit in today_units],
                unit_count=len(today_units),
            )
            break

    route_cards = []
    for path in ongoing:
        progress = (path.completed_units / path.total_units * 100) if path.total_units else 0
        next_unit = next((unit.unit_title for unit in path.units if unit.status != "done"), None)
        route_cards.append(
            RouteCard(
                id=path.id,
                title=path.title,
                type=path.type,
                progress=round(progress, 2),
                completed_units=path.completed_units,
                total_units=path.total_units,
                next_unit=next_unit,
            )
        )

    today = date.today()
    today_reviews: list[ReviewItem] = []
    for path in ongoing:
        for unit in path.units:
            if not unit.review_needed or unit.status != "done":
                continue
            if unit.last_reviewed_at and unit.last_reviewed_at.date() >= today:
                continue
            today_reviews.append(
                ReviewItem(
                    path_id=path.id,
                    path_title=path.title,
                    unit_id=unit.id,
                    unit_title=unit.unit_title,
                    last_reviewed_at=unit.last_reviewed_at,
                )
            )
    today_reviews = today_reviews[:10]

    weekly_goal = _build_weekly_goal(db, stats, ongoing)
    db.commit()

    return DashboardResponse(
        title="今天继续推进你的学习主线",
        ongoing_paths=len(ongoing),
        completed_units=stats.completed_units,
        total_xp=stats.total_xp,
        completed_paths=len(completed),
        current_level=stats.current_level,
        current_streak=stats.current_streak,
        today_task=today_task,
        motivation=random.choice(MOTIVATIONS),
        routes=route_cards,
        today_reviews=today_reviews,
        weekly_goal=weekly_goal,
    )


@router.put("/weekly-goal", response_model=WeeklyGoal)
def update_weekly_goal(payload: WeeklyGoalUpdateRequest, db: Session = Depends(get_db)):
    stats = db.get(UserStats, 1)
    stats.week_goal_target = max(1, min(payload.target, 99))
    stats.week_goal_start = _current_week_start(date.today())
    weekly_goal = _build_weekly_goal(
        db, stats, [path for path in db.query(LearningPath).all() if path.status == "ongoing"]
    )
    db.commit()
    return weekly_goal
