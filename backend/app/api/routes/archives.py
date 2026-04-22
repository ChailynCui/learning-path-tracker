from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.entities import Archive, LearningPath
from app.schemas.archive import ArchiveResponse

router = APIRouter()


@router.get("", response_model=list[ArchiveResponse])
def list_archives(db: Session = Depends(get_db)):
    archives = db.query(Archive).order_by(Archive.created_at.desc()).all()
    response: list[ArchiveResponse] = []
    for item in archives:
        path = db.query(LearningPath).filter(LearningPath.id == item.path_id).first()
        if not path:
            continue
        response.append(
            ArchiveResponse(
                id=item.id,
                path_id=item.path_id,
                path_title=path.title,
                path_type=path.type,
                source_url=path.source_url,
                start_date=path.start_date,
                end_date=path.end_date,
                total_units=path.total_units,
                completed_units=path.completed_units,
                summary_title=item.summary_title,
                what_i_learned=item.what_i_learned,
                key_points=item.key_points,
                difficult_parts=item.difficult_parts,
                mastered_parts=item.mastered_parts,
                next_steps=item.next_steps,
                created_at=item.created_at,
            )
        )
    return response


@router.get("/{archive_id}", response_model=ArchiveResponse)
def get_archive(archive_id: int, db: Session = Depends(get_db)):
    item = db.query(Archive).filter(Archive.id == archive_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Archive not found.")

    path = db.query(LearningPath).filter(LearningPath.id == item.path_id).first()
    if not path:
        raise HTTPException(status_code=404, detail="Path not found.")

    return ArchiveResponse(
        id=item.id,
        path_id=item.path_id,
        path_title=path.title,
        path_type=path.type,
        source_url=path.source_url,
        start_date=path.start_date,
        end_date=path.end_date,
        total_units=path.total_units,
        completed_units=path.completed_units,
        summary_title=item.summary_title,
        what_i_learned=item.what_i_learned,
        key_points=item.key_points,
        difficult_parts=item.difficult_parts,
        mastered_parts=item.mastered_parts,
        next_steps=item.next_steps,
        created_at=item.created_at,
    )
