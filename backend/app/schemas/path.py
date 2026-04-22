from datetime import date, datetime

from pydantic import BaseModel, Field


class CreatePathRequest(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    type: str = Field(pattern="^(tutorial|open_source)$")
    source_url: str = ""
    description: str = ""
    daily_rule: str = "1 chapter/day"
    rule_type: str = Field(default="count", pattern="^(count|range|interval)$")
    daily_chapter_count: int = 1
    interval_days: int = 1
    range_start: int | None = None
    range_end: int | None = None
    units: list[str] = Field(min_length=1)


class UnitResponse(BaseModel):
    id: int
    unit_order: int
    unit_title: str
    status: str
    planned_days: int
    completed_at: datetime | None
    summary: str
    difficulty_note: str
    review_needed: bool

    class Config:
        from_attributes = True


class PathSummaryResponse(BaseModel):
    id: int
    title: str
    type: str
    status: str
    total_units: int
    completed_units: int
    next_unit: str | None


class PathDetailResponse(BaseModel):
    id: int
    title: str
    type: str
    source_url: str
    description: str
    daily_rule: str
    rule_type: str
    daily_chapter_count: int
    interval_days: int
    range_start: int | None
    range_end: int | None
    status: str
    total_units: int
    completed_units: int
    start_date: date | None
    end_date: date | None
    units: list[UnitResponse]


class CompleteUnitRequest(BaseModel):
    study_minutes: int = 0
    comment: str = ""
    summary: str = ""
    difficulty_note: str = ""
    review_needed: bool = False


class UpdateRuleRequest(BaseModel):
    rule_type: str = Field(pattern="^(count|range|interval)$")
    daily_chapter_count: int = 1
    interval_days: int = 1
    range_start: int | None = None
    range_end: int | None = None


class UpdateRuleResponse(BaseModel):
    path_id: int
    daily_rule: str
    rule_type: str
    daily_chapter_count: int
    interval_days: int
    range_start: int | None
    range_end: int | None


class UpdateUnitPlanRequest(BaseModel):
    planned_days: int = Field(ge=1, le=30)


class UpdateUnitPlanResponse(BaseModel):
    unit_id: int
    planned_days: int


class CompleteUnitResponse(BaseModel):
    unit_id: int
    xp_gained: int
    total_xp: int
    current_level: int
    current_streak: int
    completed_units: int
    path_completed: bool


class PathLogResponse(BaseModel):
    id: int
    unit_id: int
    unit_title: str
    log_date: date
    study_minutes: int
    xp_gained: int
    comment: str


class ReviewUnitRequest(BaseModel):
    study_minutes: int = 0
    comment: str = ""


class ReviewUnitResponse(BaseModel):
    unit_id: int
    review_count: int
    last_reviewed_at: datetime | None
    current_streak: int


class MarkReviewResponse(BaseModel):
    unit_id: int
    review_needed: bool


class TimerStartRequest(BaseModel):
    unit_id: int


class TimerStatusResponse(BaseModel):
    status: str
    path_id: int | None
    unit_id: int | None
    elapsed_seconds: int
    elapsed_minutes: int


class TimerStopResponse(TimerStatusResponse):
    suggested_minutes: int
