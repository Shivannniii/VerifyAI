from sqlalchemy import Column, Integer, Text, String, ForeignKey, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.database import Base


class Claim(Base):
    __tablename__ = "claims"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    research_id = Column(
        Integer,
        ForeignKey("research_papers.id"),
        nullable=False
    )

    claim_text = Column(
        Text,
        nullable=False
    )

    status = Column(
        String(50),
        default="pending"
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    research = relationship(
        "ResearchPaper",
        back_populates="claims"
    )

    verification = relationship(
        "Verification",
        back_populates="claim",
        uselist=False,
        cascade="all, delete-orphan"
    )