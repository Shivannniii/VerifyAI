import json
from app.models.claim import Claim

VERIFIED_STATUSES = {"potentially_supported", "partially_supported", "supported", "contradicted", "insufficient_evidence", "uncertain"}

def parse_sources(raw):
    if not raw: return []
    try: return json.loads(raw)
    except Exception: return []

def serialize_claim(claim: Claim):
    v = claim.verification
    return {"id": claim.id, "research_id": claim.research_id, "claim_text": claim.claim_text, "status": claim.status, "created_at": claim.created_at, "verification": None if not v else {"id": v.id, "status": v.status, "confidence": v.confidence, "explanation": v.explanation, "sources": parse_sources(v.source), "created_at": v.created_at}}
