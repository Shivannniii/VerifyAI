from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.database import Base


class ResearchPaper(Base):
    __tablename__ = "research_papers"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=True
    )

    filename = Column(
        String(255),
        nullable=False
    )

    file_path = Column(
        String(500),
        nullable=True
    )

    extracted_text = Column(
        Text,
        nullable=True
    )

    status = Column(
        String(50),
        default="uploaded"
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    claims = relationship(
        "Claim",
        back_populates="research",
        cascade="all, delete-orphan"
    )