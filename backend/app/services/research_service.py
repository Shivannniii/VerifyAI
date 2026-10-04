from sqlalchemy.orm import Session

from app.models.research import ResearchPaper


def create_research_record(
    db: Session,
    filename: str,
    file_path: str | None = None,
    extracted_text: str | None = None,
    user_id: int | None = None
):
    research = ResearchPaper(
        filename=filename,
        file_path=file_path,
        extracted_text=extracted_text,
        user_id=user_id,
        status="uploaded"
    )

    db.add(research)
    db.commit()
    db.refresh(research)

    return research


def get_research(
    db: Session,
    research_id: int
):
    return (
        db.query(ResearchPaper)
        .filter(
            ResearchPaper.id == research_id
        )
        .first()
    )


def get_user_research(
    db: Session,
    user_id: int
):
    return (
        db.query(ResearchPaper)
        .filter(
            ResearchPaper.user_id == user_id
        )
        .order_by(
            ResearchPaper.created_at.desc()
        )
        .all()
    )