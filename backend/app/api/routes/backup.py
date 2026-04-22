from datetime import date, datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.entities import Archive, LearningLog, LearningPath, LearningUnit, UserStats
from app.schemas.backup import BackupImportRequest

router = APIRouter()


def _normalize_value(value):
    if isinstance(value, (date, datetime)):
        return value.isoformat()
    return value


def _model_rows(items: list) -> list[dict]:
    rows = []
    for item in items:
        row = {
            column.name: _normalize_value(getattr(item, column.name))
            for column in item.__table__.columns
        }
        rows.append(row)
    return rows


def _parse_date(value):
    if not value:
        return None
    return date.fromisoformat(value)


def _parse_datetime(value):
    if not value:
        return None
    return datetime.fromisoformat(value)


@router.get("/export")
def export_backup(db: Session = Depends(get_db)):
    payload = {
        "version": 1,
        "exported_at": datetime.utcnow().isoformat(),
        "data": {
            "learning_paths": _model_rows(db.query(LearningPath).all()),
            "learning_units": _model_rows(db.query(LearningUnit).all()),
            "learning_logs": _model_rows(db.query(LearningLog).all()),
            "archives": _model_rows(db.query(Archive).all()),
            "user_stats": _model_rows(db.query(UserStats).all()),
        },
    }
    return payload


@router.post("/import")
def import_backup(payload: BackupImportRequest, db: Session = Depends(get_db)):
    data = payload.data
    required = {"learning_paths", "learning_units", "learning_logs", "archives", "user_stats"}
    if not required.issubset(data.keys()):
        raise HTTPException(status_code=422, detail="Backup JSON missing required tables.")

    db.query(LearningLog).delete()
    db.query(Archive).delete()
    db.query(LearningUnit).delete()
    db.query(LearningPath).delete()
    db.query(UserStats).delete()
    db.commit()

    for row in data.get("learning_paths", []):
        db.add(
            LearningPath(
                id=row.get("id"),
                title=row.get("title", ""),
                type=row.get("type", "tutorial"),
                source_url=row.get("source_url", ""),
                description=row.get("description", ""),
                daily_rule=row.get("daily_rule", "1 chapter/day"),
                rule_type=row.get("rule_type", "count"),
                daily_chapter_count=row.get("daily_chapter_count", 1),
                interval_days=row.get("interval_days", 1),
                range_start=row.get("range_start"),
                range_end=row.get("range_end"),
                total_units=row.get("total_units", 0),
                completed_units=row.get("completed_units", 0),
                status=row.get("status", "ongoing"),
                start_date=_parse_date(row.get("start_date")),
                end_date=_parse_date(row.get("end_date")),
                created_at=_parse_datetime(row.get("created_at")) or datetime.utcnow(),
                updated_at=_parse_datetime(row.get("updated_at")) or datetime.utcnow(),
            )
        )

    for row in data.get("learning_units", []):
        db.add(
            LearningUnit(
                id=row.get("id"),
                path_id=row.get("path_id"),
                unit_order=row.get("unit_order", 0),
                unit_title=row.get("unit_title", ""),
                unit_type=row.get("unit_type", "chapter"),
                status=row.get("status", "pending"),
                planned_days=row.get("planned_days", 1),
                completed_at=_parse_datetime(row.get("completed_at")),
                summary=row.get("summary", ""),
                difficulty_note=row.get("difficulty_note", ""),
                review_needed=bool(row.get("review_needed", False)),
                last_reviewed_at=_parse_datetime(row.get("last_reviewed_at")),
                review_count=row.get("review_count", 0),
            )
        )

    for row in data.get("learning_logs", []):
        db.add(
            LearningLog(
                id=row.get("id"),
                path_id=row.get("path_id"),
                unit_id=row.get("unit_id"),
                log_date=_parse_date(row.get("log_date")) or date.today(),
                study_minutes=row.get("study_minutes", 0),
                xp_gained=row.get("xp_gained", 0),
                comment=row.get("comment", ""),
            )
        )

    for row in data.get("archives", []):
        db.add(
            Archive(
                id=row.get("id"),
                path_id=row.get("path_id"),
                summary_title=row.get("summary_title", ""),
                what_i_learned=row.get("what_i_learned", ""),
                key_points=row.get("key_points", ""),
                difficult_parts=row.get("difficult_parts", ""),
                mastered_parts=row.get("mastered_parts", ""),
                next_steps=row.get("next_steps", ""),
                created_at=_parse_datetime(row.get("created_at")) or datetime.utcnow(),
            )
        )

    for row in data.get("user_stats", []):
        db.add(
            UserStats(
                id=row.get("id"),
                total_xp=row.get("total_xp", 0),
                current_level=row.get("current_level", 1),
                current_streak=row.get("current_streak", 0),
                max_streak=row.get("max_streak", 0),
                completed_paths=row.get("completed_paths", 0),
                completed_units=row.get("completed_units", 0),
                week_goal_target=row.get("week_goal_target", 5),
                week_goal_start=_parse_date(row.get("week_goal_start")),
                timer_path_id=row.get("timer_path_id"),
                timer_unit_id=row.get("timer_unit_id"),
                timer_status=row.get("timer_status", "idle"),
                timer_started_at=_parse_datetime(row.get("timer_started_at")),
                timer_elapsed_seconds=row.get("timer_elapsed_seconds", 0),
                timer_updated_at=_parse_datetime(row.get("timer_updated_at")),
            )
        )

    if not data.get("user_stats"):
        db.add(UserStats(id=1, week_goal_target=5, week_goal_start=date.today()))

    db.commit()
    return {"ok": True, "message": "Backup imported successfully."}
