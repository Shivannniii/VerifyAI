from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models.research import ResearchPaper
from app.models.user import User


router = APIRouter(
    prefix="/user",
    tags=["User"]
)


@router.get("/{user_id}/research")
def get_user_research(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Previously anyone could read any user's papers by changing the id.
    if user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only view your own research papers.",
        )

    research_papers = (
        db.query(ResearchPaper)
        .filter(ResearchPaper.user_id == user_id)
        .order_by(
            ResearchPaper.created_at.desc(),
            ResearchPaper.id.desc(),
        )
        .all()
    )

    return [
        {
            "id": paper.id,
            "user_id": paper.user_id,
            "filename": paper.filename,
            "status": paper.status,
            "created_at": paper.created_at
        }
        for paper in research_papers
    ]
