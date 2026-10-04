from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime


class ResearchResponse(BaseModel):
    id: int
    filename: str
    status: str
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class ResearchUploadResponse(BaseModel):
    message: str
    filename: str
    text_length: int
    text_preview: str