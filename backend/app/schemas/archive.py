from datetime import date, datetime

from pydantic import BaseModel


class ArchiveResponse(BaseModel):
    id: int
    path_id: int
    path_title: str
    path_type: str
    source_url: str
    start_date: date | None
    end_date: date | None
    total_units: int
    completed_units: int
    summary_title: str
    what_i_learned: str
    key_points: str
    difficult_parts: str
    mastered_parts: str
    next_steps: str
    created_at: datetime
