from datetime import date, datetime

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class LearningPath(Base):
    __tablename__ = "learning_paths"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    type: Mapped[str] = mapped_column(String(50), nullable=False)
    source_url: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[str] = mapped_column(Text, default="")
    daily_rule: Mapped[str] = mapped_column(String(60), default="1 chapter/day")
    rule_type: Mapped[str] = mapped_column(String(20), default="count")
    daily_chapter_count: Mapped[int] = mapped_column(Integer, default=1)
    interval_days: Mapped[int] = mapped_column(Integer, default=1)
    range_start: Mapped[int | None] = mapped_column(Integer, nullable=True)
    range_end: Mapped[int | None] = mapped_column(Integer, nullable=True)
    total_units: Mapped[int] = mapped_column(Integer, default=0)
    completed_units: Mapped[int] = mapped_column(Integer, default=0)
    status: Mapped[str] = mapped_column(String(30), default="ongoing")
    start_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    end_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    units: Mapped[list["LearningUnit"]] = relationship(
        back_populates="path", cascade="all, delete-orphan", order_by="LearningUnit.unit_order"
    )
    logs: Mapped[list["LearningLog"]] = relationship(
        back_populates="path", cascade="all, delete-orphan"
    )
    archive: Mapped["Archive | None"] = relationship(back_populates="path", uselist=False)


class LearningUnit(Base):
    __tablename__ = "learning_units"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    path_id: Mapped[int] = mapped_column(ForeignKey("learning_paths.id"), nullable=False)
    unit_order: Mapped[int] = mapped_column(Integer, nullable=False)
    unit_title: Mapped[str] = mapped_column(String(300), nullable=False)
    unit_type: Mapped[str] = mapped_column(String(50), default="chapter")
    status: Mapped[str] = mapped_column(String(30), default="pending")
    completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    summary: Mapped[str] = mapped_column(Text, default="")
    difficulty_note: Mapped[str] = mapped_column(Text, default="")
    review_needed: Mapped[bool] = mapped_column(Boolean, default=False)
    planned_days: Mapped[int] = mapped_column(Integer, default=1)
    last_reviewed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    review_count: Mapped[int] = mapped_column(Integer, default=0)

    path: Mapped["LearningPath"] = relationship(back_populates="units")
    logs: Mapped[list["LearningLog"]] = relationship(back_populates="unit")


class LearningLog(Base):
    __tablename__ = "learning_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    path_id: Mapped[int] = mapped_column(ForeignKey("learning_paths.id"), nullable=False)
    unit_id: Mapped[int] = mapped_column(ForeignKey("learning_units.id"), nullable=False)
    log_date: Mapped[date] = mapped_column(Date, nullable=False)
    study_minutes: Mapped[int] = mapped_column(Integer, default=0)
    xp_gained: Mapped[int] = mapped_column(Integer, default=0)
    comment: Mapped[str] = mapped_column(Text, default="")

    path: Mapped["LearningPath"] = relationship(back_populates="logs")
    unit: Mapped["LearningUnit"] = relationship(back_populates="logs")


class Archive(Base):
    __tablename__ = "archives"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    path_id: Mapped[int] = mapped_column(ForeignKey("learning_paths.id"), nullable=False, unique=True)
    summary_title: Mapped[str] = mapped_column(String(200), default="")
    what_i_learned: Mapped[str] = mapped_column(Text, default="")
    key_points: Mapped[str] = mapped_column(Text, default="")
    difficult_parts: Mapped[str] = mapped_column(Text, default="")
    mastered_parts: Mapped[str] = mapped_column(Text, default="")
    next_steps: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    path: Mapped["LearningPath"] = relationship(back_populates="archive")


class UserStats(Base):
    __tablename__ = "user_stats"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    total_xp: Mapped[int] = mapped_column(Integer, default=0)
    current_level: Mapped[int] = mapped_column(Integer, default=1)
    current_streak: Mapped[int] = mapped_column(Integer, default=0)
    max_streak: Mapped[int] = mapped_column(Integer, default=0)
    completed_paths: Mapped[int] = mapped_column(Integer, default=0)
    completed_units: Mapped[int] = mapped_column(Integer, default=0)
    week_goal_target: Mapped[int] = mapped_column(Integer, default=5)
    week_goal_start: Mapped[date | None] = mapped_column(Date, nullable=True)
    timer_path_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    timer_unit_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    timer_status: Mapped[str] = mapped_column(String(20), default="idle")
    timer_started_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    timer_elapsed_seconds: Mapped[int] = mapped_column(Integer, default=0)
    timer_updated_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
