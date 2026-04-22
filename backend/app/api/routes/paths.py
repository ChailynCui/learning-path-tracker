from datetime import date, datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.entities import LearningLog, LearningPath, LearningUnit, UserStats
from app.schemas.path import (
    CompleteUnitRequest,
    CompleteUnitResponse,
    CreatePathRequest,
    MarkReviewResponse,
    PathDetailResponse,
    PathLogResponse,
    PathSummaryResponse,
    ReviewUnitRequest,
    ReviewUnitResponse,
    TimerStartRequest,
    TimerStatusResponse,
    TimerStopResponse,
    UnitResponse,
    UpdateUnitPlanRequest,
    UpdateUnitPlanResponse,
    UpdateRuleRequest,
    UpdateRuleResponse,
)
from app.services.archive_service import build_archive_for_path
from app.services.gamification import apply_daily_streak, level_from_xp, reward_for_unit_completion

router = APIRouter()


def _timer_elapsed_seconds(stats: UserStats) -> int:
    elapsed = stats.timer_elapsed_seconds or 0
    if stats.timer_status == "running" and stats.timer_started_at:
        elapsed += max(int((datetime.now() - stats.timer_started_at).total_seconds()), 0)
    return elapsed


def _timer_response(stats: UserStats) -> TimerStatusResponse:
    elapsed_seconds = _timer_elapsed_seconds(stats)
    elapsed_minutes = max(round(elapsed_seconds / 60), 0)
    return TimerStatusResponse(
        status=stats.timer_status or "idle",
        path_id=stats.timer_path_id,
        unit_id=stats.timer_unit_id,
        elapsed_seconds=elapsed_seconds,
        elapsed_minutes=elapsed_minutes,
    )


def _next_unit_title(path: LearningPath) -> str | None:
    for unit in path.units:
        if unit.status != "done":
            return unit.unit_title
    return None


def _normalize_rule(
    rule_type: str,
    daily_chapter_count: int,
    interval_days: int,
    range_start: int | None,
    range_end: int | None,
    total_units: int,
) -> tuple[str, str, int, int, int | None, int | None]:
    if rule_type == "range":
        if range_start is None or range_end is None:
            raise HTTPException(status_code=422, detail="Range rule requires start and end chapter.")
        start = max(int(range_start), 1)
        end = min(int(range_end), total_units)
        if start > end:
            raise HTTPException(status_code=422, detail="Invalid range: start must be <= end.")
        return (
            f"chapter {start}-{end}",
            "range",
            max(end - start + 1, 1),
            1,
            start,
            end,
        )

    if rule_type == "interval":
        days = max(int(interval_days), 1)
        return (f"1 chapter/{days} day", "interval", 1, days, None, None)

    count = max(int(daily_chapter_count), 1)
    return (f"{count} chapter/day", "count", count, 1, None, None)


@router.post("", response_model=PathDetailResponse)
def create_path(payload: CreatePathRequest, db: Session = Depends(get_db)):
    chapters = [unit.strip() for unit in payload.units if unit.strip()]
    if not chapters:
        raise HTTPException(status_code=422, detail="At least one chapter is required.")
    total_units = len(chapters)
    daily_rule, rule_type, daily_count, interval_days, range_start, range_end = _normalize_rule(
        payload.rule_type,
        payload.daily_chapter_count,
        payload.interval_days,
        payload.range_start,
        payload.range_end,
        total_units,
    )

    path = LearningPath(
        title=payload.title,
        type=payload.type,
        source_url=payload.source_url.strip(),
        description=payload.description,
        daily_rule=daily_rule,
        rule_type=rule_type,
        daily_chapter_count=daily_count,
        interval_days=interval_days,
        range_start=range_start,
        range_end=range_end,
        total_units=total_units,
        completed_units=0,
        status="ongoing",
        start_date=date.today(),
    )
    db.add(path)
    db.flush()

    for idx, chapter in enumerate(chapters, start=1):
        db.add(
            LearningUnit(
                path_id=path.id,
                unit_order=idx,
                unit_title=chapter,
                unit_type="chapter",
                planned_days=max(interval_days, 1) if rule_type == "interval" else 1,
            )
        )

    db.commit()
    db.refresh(path)
    return PathDetailResponse(
        id=path.id,
        title=path.title,
        type=path.type,
        source_url=path.source_url,
        description=path.description,
        daily_rule=path.daily_rule,
        rule_type=path.rule_type,
        daily_chapter_count=path.daily_chapter_count,
        interval_days=path.interval_days,
        range_start=path.range_start,
        range_end=path.range_end,
        status=path.status,
        total_units=path.total_units,
        completed_units=path.completed_units,
        start_date=path.start_date,
        end_date=path.end_date,
        units=[UnitResponse.model_validate(unit) for unit in path.units],
    )


@router.get("", response_model=list[PathSummaryResponse])
def list_paths(db: Session = Depends(get_db)):
    paths = db.query(LearningPath).order_by(LearningPath.created_at.desc()).all()
    return [
        PathSummaryResponse(
            id=path.id,
            title=path.title,
            type=path.type,
            status=path.status,
            total_units=path.total_units,
            completed_units=path.completed_units,
            next_unit=_next_unit_title(path),
        )
        for path in paths
    ]


@router.get("/{path_id}", response_model=PathDetailResponse)
def get_path(path_id: int, db: Session = Depends(get_db)):
    path = db.query(LearningPath).filter(LearningPath.id == path_id).first()
    if not path:
        raise HTTPException(status_code=404, detail="Path not found.")

    return PathDetailResponse(
        id=path.id,
        title=path.title,
        type=path.type,
        source_url=path.source_url,
        description=path.description,
        daily_rule=path.daily_rule,
        rule_type=path.rule_type,
        daily_chapter_count=path.daily_chapter_count,
        interval_days=path.interval_days,
        range_start=path.range_start,
        range_end=path.range_end,
        status=path.status,
        total_units=path.total_units,
        completed_units=path.completed_units,
        start_date=path.start_date,
        end_date=path.end_date,
        units=[UnitResponse.model_validate(unit) for unit in path.units],
    )


@router.get("/{path_id}/logs", response_model=list[PathLogResponse])
def list_path_logs(path_id: int, db: Session = Depends(get_db)):
    path = db.query(LearningPath).filter(LearningPath.id == path_id).first()
    if not path:
        raise HTTPException(status_code=404, detail="Path not found.")

    logs = (
        db.query(LearningLog)
        .filter(LearningLog.path_id == path_id)
        .order_by(LearningLog.log_date.desc(), LearningLog.id.desc())
        .all()
    )
    units = {unit.id: unit.unit_title for unit in path.units}
    return [
        PathLogResponse(
            id=log.id,
            unit_id=log.unit_id,
            unit_title=units.get(log.unit_id, ""),
            log_date=log.log_date,
            study_minutes=log.study_minutes,
            xp_gained=log.xp_gained,
            comment=log.comment,
        )
        for log in logs
    ]


@router.put("/{path_id}/rule", response_model=UpdateRuleResponse)
def update_path_rule(path_id: int, payload: UpdateRuleRequest, db: Session = Depends(get_db)):
    path = db.query(LearningPath).filter(LearningPath.id == path_id).first()
    if not path:
        raise HTTPException(status_code=404, detail="Path not found.")

    daily_rule, rule_type, daily_count, interval_days, range_start, range_end = _normalize_rule(
        payload.rule_type,
        payload.daily_chapter_count,
        payload.interval_days,
        payload.range_start,
        payload.range_end,
        path.total_units,
    )
    path.daily_rule = daily_rule
    path.rule_type = rule_type
    path.daily_chapter_count = daily_count
    path.interval_days = interval_days
    path.range_start = range_start
    path.range_end = range_end
    if rule_type == "interval":
        path.start_date = date.today()
    path.updated_at = datetime.now()
    db.commit()

    return UpdateRuleResponse(
        path_id=path.id,
        daily_rule=path.daily_rule,
        rule_type=path.rule_type,
        daily_chapter_count=path.daily_chapter_count,
        interval_days=path.interval_days,
        range_start=path.range_start,
        range_end=path.range_end,
    )


@router.put("/{path_id}/units/{unit_id}/plan-days", response_model=UpdateUnitPlanResponse)
def update_unit_plan_days(
    path_id: int,
    unit_id: int,
    payload: UpdateUnitPlanRequest,
    db: Session = Depends(get_db),
):
    path = db.query(LearningPath).filter(LearningPath.id == path_id).first()
    if not path:
        raise HTTPException(status_code=404, detail="Path not found.")
    unit = (
        db.query(LearningUnit)
        .filter(LearningUnit.id == unit_id, LearningUnit.path_id == path_id)
        .first()
    )
    if not unit:
        raise HTTPException(status_code=404, detail="Unit not found.")

    unit.planned_days = max(1, min(payload.planned_days, 30))
    path.updated_at = datetime.now()
    db.commit()
    return UpdateUnitPlanResponse(unit_id=unit.id, planned_days=unit.planned_days)


@router.post("/{path_id}/units/{unit_id}/mark-review", response_model=MarkReviewResponse)
def mark_unit_for_review(path_id: int, unit_id: int, db: Session = Depends(get_db)):
    path = db.query(LearningPath).filter(LearningPath.id == path_id).first()
    if not path:
        raise HTTPException(status_code=404, detail="Path not found.")

    unit = (
        db.query(LearningUnit)
        .filter(LearningUnit.id == unit_id, LearningUnit.path_id == path_id)
        .first()
    )
    if not unit:
        raise HTTPException(status_code=404, detail="Unit not found.")
    if unit.status != "done":
        raise HTTPException(status_code=422, detail="Only completed chapters can be added to review.")

    unit.review_needed = True
    path.updated_at = datetime.now()
    db.commit()

    return MarkReviewResponse(unit_id=unit.id, review_needed=unit.review_needed)


@router.post("/{path_id}/units/{unit_id}/review", response_model=ReviewUnitResponse)
def review_unit(
    path_id: int,
    unit_id: int,
    payload: ReviewUnitRequest,
    db: Session = Depends(get_db),
):
    path = db.query(LearningPath).filter(LearningPath.id == path_id).first()
    if not path:
        raise HTTPException(status_code=404, detail="Path not found.")

    unit = (
        db.query(LearningUnit)
        .filter(LearningUnit.id == unit_id, LearningUnit.path_id == path_id)
        .first()
    )
    if not unit:
        raise HTTPException(status_code=404, detail="Unit not found.")
    if unit.status != "done":
        raise HTTPException(status_code=422, detail="Only completed chapters can be reviewed.")

    stats = db.get(UserStats, 1)
    today = date.today()
    last_log_date = db.query(func.max(LearningLog.log_date)).scalar()
    streak_delta, _ = apply_daily_streak(last_log_date, today)
    if streak_delta == 1:
        stats.current_streak += 1
    elif streak_delta == -1:
        stats.current_streak = 1
    stats.max_streak = max(stats.max_streak, stats.current_streak)

    unit.review_needed = False
    unit.last_reviewed_at = datetime.now()
    unit.review_count += 1

    db.add(
        LearningLog(
            path_id=path.id,
            unit_id=unit.id,
            log_date=today,
            study_minutes=max(payload.study_minutes, 0),
            xp_gained=0,
            comment=(payload.comment or f"复习：{unit.unit_title}").strip(),
        )
    )
    db.commit()

    return ReviewUnitResponse(
        unit_id=unit.id,
        review_count=unit.review_count,
        last_reviewed_at=unit.last_reviewed_at,
        current_streak=stats.current_streak,
    )


@router.get("/{path_id}/timer", response_model=TimerStatusResponse)
def get_timer_status(path_id: int, db: Session = Depends(get_db)):
    path = db.query(LearningPath).filter(LearningPath.id == path_id).first()
    if not path:
        raise HTTPException(status_code=404, detail="Path not found.")
    stats = db.get(UserStats, 1)
    response = _timer_response(stats)
    if response.path_id and response.path_id != path_id and response.status in {"running", "paused"}:
        response.status = "locked"
    return response


@router.post("/{path_id}/timer/start", response_model=TimerStatusResponse)
def start_timer(path_id: int, payload: TimerStartRequest, db: Session = Depends(get_db)):
    path = db.query(LearningPath).filter(LearningPath.id == path_id).first()
    if not path:
        raise HTTPException(status_code=404, detail="Path not found.")
    unit = (
        db.query(LearningUnit)
        .filter(LearningUnit.id == payload.unit_id, LearningUnit.path_id == path_id)
        .first()
    )
    if not unit:
        raise HTTPException(status_code=404, detail="Unit not found.")

    stats = db.get(UserStats, 1)
    if (
        stats.timer_status in {"running", "paused"}
        and stats.timer_path_id
        and stats.timer_path_id != path_id
    ):
        raise HTTPException(status_code=409, detail="Another timer is active on a different path.")

    stats.timer_path_id = path_id
    stats.timer_unit_id = payload.unit_id
    stats.timer_status = "running"
    stats.timer_elapsed_seconds = 0
    stats.timer_started_at = datetime.now()
    stats.timer_updated_at = datetime.now()
    db.commit()
    return _timer_response(stats)


@router.post("/{path_id}/timer/pause", response_model=TimerStatusResponse)
def pause_timer(path_id: int, db: Session = Depends(get_db)):
    stats = db.get(UserStats, 1)
    if stats.timer_path_id != path_id or stats.timer_status != "running":
        raise HTTPException(status_code=409, detail="No running timer for this path.")

    stats.timer_elapsed_seconds = _timer_elapsed_seconds(stats)
    stats.timer_started_at = None
    stats.timer_status = "paused"
    stats.timer_updated_at = datetime.now()
    db.commit()
    return _timer_response(stats)


@router.post("/{path_id}/timer/resume", response_model=TimerStatusResponse)
def resume_timer(path_id: int, db: Session = Depends(get_db)):
    stats = db.get(UserStats, 1)
    if stats.timer_path_id != path_id or stats.timer_status != "paused":
        raise HTTPException(status_code=409, detail="No paused timer for this path.")

    stats.timer_status = "running"
    stats.timer_started_at = datetime.now()
    stats.timer_updated_at = datetime.now()
    db.commit()
    return _timer_response(stats)


@router.post("/{path_id}/timer/stop", response_model=TimerStopResponse)
def stop_timer(path_id: int, db: Session = Depends(get_db)):
    stats = db.get(UserStats, 1)
    if stats.timer_path_id != path_id or stats.timer_status not in {"running", "paused"}:
        raise HTTPException(status_code=409, detail="No active timer for this path.")

    elapsed_seconds = _timer_elapsed_seconds(stats)
    suggested_minutes = max(round(elapsed_seconds / 60), 1) if elapsed_seconds else 0
    unit_id = stats.timer_unit_id

    stats.timer_status = "idle"
    stats.timer_path_id = None
    stats.timer_unit_id = None
    stats.timer_started_at = None
    stats.timer_elapsed_seconds = 0
    stats.timer_updated_at = datetime.now()
    db.commit()

    return TimerStopResponse(
        status="idle",
        path_id=path_id,
        unit_id=unit_id,
        elapsed_seconds=elapsed_seconds,
        elapsed_minutes=max(round(elapsed_seconds / 60), 0),
        suggested_minutes=suggested_minutes,
    )


@router.post("/{path_id}/units/{unit_id}/complete", response_model=CompleteUnitResponse)
def complete_unit(
    path_id: int,
    unit_id: int,
    payload: CompleteUnitRequest,
    db: Session = Depends(get_db),
):
    path = db.query(LearningPath).filter(LearningPath.id == path_id).first()
    if not path:
        raise HTTPException(status_code=404, detail="Path not found.")

    unit = (
        db.query(LearningUnit)
        .filter(LearningUnit.id == unit_id, LearningUnit.path_id == path_id)
        .first()
    )
    if not unit:
        raise HTTPException(status_code=404, detail="Unit not found.")

    if unit.status == "done":
        stats = db.get(UserStats, 1)
        return CompleteUnitResponse(
            unit_id=unit.id,
            xp_gained=0,
            total_xp=stats.total_xp,
            current_level=stats.current_level,
            current_streak=stats.current_streak,
            completed_units=stats.completed_units,
            path_completed=path.status == "completed",
        )

    stats = db.get(UserStats, 1)
    today = date.today()
    last_log_date = db.query(func.max(LearningLog.log_date)).scalar()
    reward = reward_for_unit_completion(stats.current_streak, last_log_date, today)

    unit.status = "done"
    unit.completed_at = datetime.now()
    unit.summary = payload.summary
    unit.difficulty_note = payload.difficulty_note
    unit.review_needed = payload.review_needed

    path.completed_units += 1
    path.updated_at = datetime.now()

    path_completed = path.completed_units >= path.total_units
    if path_completed:
        path.status = "completed"
        path.end_date = today
        reward.xp_gained += 100
        stats.completed_paths += 1
        build_archive_for_path(db, path)

    stats.total_xp += reward.xp_gained
    stats.current_streak = reward.streak
    stats.max_streak = max(stats.max_streak, reward.streak)
    stats.completed_units += 1
    stats.current_level = level_from_xp(stats.total_xp)

    db.add(
        LearningLog(
            path_id=path.id,
            unit_id=unit.id,
            log_date=today,
            study_minutes=payload.study_minutes,
            xp_gained=reward.xp_gained,
            comment=payload.comment,
        )
    )
    db.commit()

    return CompleteUnitResponse(
        unit_id=unit.id,
        xp_gained=reward.xp_gained,
        total_xp=stats.total_xp,
        current_level=stats.current_level,
        current_streak=stats.current_streak,
        completed_units=stats.completed_units,
        path_completed=path_completed,
    )
