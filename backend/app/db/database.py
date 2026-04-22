from datetime import date

from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import DB_PATH, DATABASE_URL
from app.db.base import Base
from app.models.entities import UserStats

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


def _column_exists(table_name: str, column_name: str) -> bool:
    with engine.connect() as conn:
        result = conn.execute(text(f"PRAGMA table_info({table_name})"))
        columns = [row[1] for row in result.fetchall()]
        return column_name in columns


def _ensure_column(table_name: str, column_name: str, column_sql: str) -> None:
    if _column_exists(table_name, column_name):
        return
    with engine.begin() as conn:
        conn.execute(text(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_sql}"))


def _ensure_backward_compatible_schema() -> None:
    # learning_paths
    _ensure_column("learning_paths", "rule_type", "VARCHAR(20) NOT NULL DEFAULT 'count'")
    _ensure_column("learning_paths", "daily_chapter_count", "INTEGER NOT NULL DEFAULT 1")
    _ensure_column("learning_paths", "interval_days", "INTEGER NOT NULL DEFAULT 1")
    _ensure_column("learning_paths", "range_start", "INTEGER")
    _ensure_column("learning_paths", "range_end", "INTEGER")

    # learning_units
    _ensure_column("learning_units", "planned_days", "INTEGER NOT NULL DEFAULT 1")
    _ensure_column("learning_units", "last_reviewed_at", "DATETIME")
    _ensure_column("learning_units", "review_count", "INTEGER NOT NULL DEFAULT 0")

    # user_stats
    _ensure_column("user_stats", "week_goal_target", "INTEGER NOT NULL DEFAULT 5")
    _ensure_column("user_stats", "week_goal_start", "DATE")
    _ensure_column("user_stats", "timer_path_id", "INTEGER")
    _ensure_column("user_stats", "timer_unit_id", "INTEGER")
    _ensure_column("user_stats", "timer_status", "VARCHAR(20) NOT NULL DEFAULT 'idle'")
    _ensure_column("user_stats", "timer_started_at", "DATETIME")
    _ensure_column("user_stats", "timer_elapsed_seconds", "INTEGER NOT NULL DEFAULT 0")
    _ensure_column("user_stats", "timer_updated_at", "DATETIME")


def init_db() -> None:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    Base.metadata.create_all(bind=engine)
    _ensure_backward_compatible_schema()

    with SessionLocal() as db:
        has_stats = db.get(UserStats, 1)
        if not has_stats:
            db.add(UserStats(id=1, week_goal_target=5, week_goal_start=date.today()))
            db.commit()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
