from datetime import datetime

from sqlalchemy.orm import Session

from app.models.entities import Archive, LearningPath


def build_archive_for_path(db: Session, path: LearningPath) -> Archive:
    existing = db.query(Archive).filter(Archive.path_id == path.id).first()
    if existing:
        return existing

    archive = Archive(
        path_id=path.id,
        summary_title=f"{path.title} 学习归档",
        what_i_learned="按章节完成了该项目的学习路线，并建立了整体知识脉络。",
        key_points="1. 核心章节结构\n2. 关键实现思路\n3. 实践与复盘节奏",
        difficult_parts="可在每章总结中补充难点，后续做二刷复习。",
        mastered_parts="已完成章节可复述主要概念与实现流程。",
        next_steps="选 1-2 个重点章节做代码实践，并整理复习清单。",
        created_at=datetime.utcnow(),
    )
    db.add(archive)
    db.flush()
    return archive
