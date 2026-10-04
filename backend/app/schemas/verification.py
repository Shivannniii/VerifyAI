from pydantic import BaseModel, ConfigDict
from typing import Optional


class VerificationResponse(BaseModel):
    id: int
    claim_id: int
    status: str
    confidence: float
    explanation: Optional[str] = None
    source: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
