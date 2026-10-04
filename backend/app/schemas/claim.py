from pydantic import BaseModel, ConfigDict


class ClaimCreate(BaseModel):
    claim_text: str


class ClaimResponse(BaseModel):
    id: int
    research_id: int
    claim_text: str
    status: str

    model_config = ConfigDict(from_attributes=True)
