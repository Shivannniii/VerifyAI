from sqlalchemy import (
    Column,
    Integer,
    Text,
    String,
    Float,
    ForeignKey,
    DateTime
)

from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.database import Base


class Verification(Base):
    __tablename__ = "verifications"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    claim_id = Column(
        Integer,
        ForeignKey("claims.id"),
        nullable=False,
        unique=True
    )

    status = Column(
        String(50),
        default="unverified"
    )

    confidence = Column(
        Float,
        default=0.0
    )

    explanation = Column(
        Text,
        nullable=True
    )

    source = Column(
        Text,
        nullable=True
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    claim = relationship(
        "Claim",
        back_populates="verification"
    )