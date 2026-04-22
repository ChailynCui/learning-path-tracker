from datetime import date, datetime

from pydantic import BaseModel, Field


class TodayTask(BaseModel):
    path_id: int | None = None
    path_title: str | None = None
    unit_id: int | None = None
    unit_title: str | None = None
    unit_ids: list[int] = Field(default_factory=list)
    unit_count: int = 0


class RouteCard(BaseModel):
    id: int
    title: str
    type: str
    progress: float
    completed_units: int
    total_units: int
    next_unit: str | None


class ReviewItem(BaseModel):
    path_id: int
    path_title: str
    unit_id: int
    unit_title: str
    last_reviewed_at: datetime | None


class WeeklyGoal(BaseModel):
    target: int
    week_start: date
    completed: int
    progress: float
    overdue_units: int
    overdue_titles: list[str]


class WeeklyGoalUpdateRequest(BaseModel):
    target: int


class DashboardResponse(BaseModel):
    title: str
    ongoing_paths: int
    completed_units: int
    total_xp: int
    completed_paths: int
    current_level: int
    current_streak: int
    today_task: TodayTask
    motivation: str
    routes: list[RouteCard]
    today_reviews: list[ReviewItem]
    weekly_goal: WeeklyGoal
