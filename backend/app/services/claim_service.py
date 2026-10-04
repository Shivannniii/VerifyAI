from sqlalchemy.orm import Session

from app.models.claim import Claim


def create_claim(
    db: Session,
    research_id: int,
    claim_text: str
):
    claim = Claim(
        research_id=research_id,
        claim_text=claim_text,
        status="pending"
    )

    db.add(claim)
    db.commit()
    db.refresh(claim)

    return claim


def get_claims_by_research(
    db: Session,
    research_id: int
):
    return (
        db.query(Claim)
        .filter(Claim.research_id == research_id)
        .all()
    )