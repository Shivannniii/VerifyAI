from sqlalchemy.orm import Session

from app.models.claim import Claim
from app.models.verification import Verification


def create_verification(
    db: Session,
    claim_id: int,
    status: str = "unverified",
    confidence: float = 0.0,
    explanation: str | None = None,
    source: str | None = None
):
    verification = Verification(
        claim_id=claim_id,
        status=status,
        confidence=confidence,
        explanation=explanation,
        source=source
    )

    db.add(verification)
    db.commit()
    db.refresh(verification)

    return verification


def update_claim_verification(
    db: Session,
    claim: Claim,
    status: str,
    confidence: float,
    explanation: str | None = None,
    source: str | None = None
):
    claim.status = status

    verification = (
        db.query(Verification)
        .filter(Verification.claim_id == claim.id)
        .first()
    )

    if verification is None:
        verification = Verification(
            claim_id=claim.id
        )

        db.add(verification)

    verification.status = status
    verification.confidence = confidence
    verification.explanation = explanation
    verification.source = source

    db.commit()
    db.refresh(verification)

    return verification