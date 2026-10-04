from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, Float, ForeignKey, DateTime
from app.database import Base

class DetectorAnalysis(Base):
    __tablename__ = "detector_analyses"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    input_type = Column(String(30), nullable=False, default="text")
    filename = Column(String(255), nullable=True)
    text = Column(Text, nullable=False)
    word_count = Column(Integer, default=0, nullable=False)
    sentence_count = Column(Integer, default=0, nullable=False)
    ai_probability = Column(Float, default=0.0, nullable=False)
    human_probability = Column(Float, default=0.0, nullable=False)
    confidence = Column(Float, default=0.0, nullable=False)
    classification = Column(String(50), nullable=False, default="uncertain")
    mode = Column(String(30), nullable=False, default="baseline")
    explanation = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
