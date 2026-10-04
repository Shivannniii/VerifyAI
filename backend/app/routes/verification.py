import json
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.dependencies import get_current_user
from app.models.claim import Claim
from app.models.research import ResearchPaper
from app.models.user import User
from app.models.verification import Verification
from app.serializers import serialize_claim, parse_sources
from app.services.source_service import SourceSearchError, verify_claim_with_sources

router=APIRouter(prefix="/verification",tags=["Verification"])
def owned(db,claim_id,user):
    c=db.query(Claim).join(ResearchPaper,Claim.research_id==ResearchPaper.id).filter(Claim.id==claim_id,ResearchPaper.user_id==user.id).first()
    if not c: raise HTTPException(404,"Claim not found")
    return c

@router.post("/{claim_id}")
def create(claim_id:int,db:Session=Depends(get_db),user:User=Depends(get_current_user)):
    c=owned(db,claim_id,user); v=db.query(Verification).filter(Verification.claim_id==claim_id).first()
    if v: return {"message":"Claim already has a verification","verification_id":v.id,"status":v.status}
    v=Verification(claim_id=claim_id,status="unverified",confidence=0,explanation="Verification pending."); db.add(v); c.status="verification_pending"; db.commit(); db.refresh(v); return {"id":v.id,"claim_id":v.claim_id,"status":v.status}

@router.post("/{claim_id}/verify")
def run(claim_id:int,db:Session=Depends(get_db),user:User=Depends(get_current_user)):
    c=owned(db,claim_id,user)
    try: result=verify_claim_with_sources(c.claim_text)
    except SourceSearchError as e: raise HTTPException(502,str(e))
    except Exception as e: raise HTTPException(500,f"Evidence verification failed: {e}")
    v=db.query(Verification).filter(Verification.claim_id==claim_id).first() or Verification(claim_id=claim_id)
    if v.id is None: db.add(v)
    v.status=result["verdict"]; v.confidence=float(result["confidence"]); v.explanation=result["explanation"]; v.source=json.dumps(result.get("sources",[]),ensure_ascii=False); c.status=result["verdict"]; db.commit(); db.refresh(c)
    return {"message":"Claim verification completed","claim":serialize_claim(c),"mode":result.get("mode","baseline") }

@router.get("/{claim_id}")
def get(claim_id:int,db:Session=Depends(get_db),user:User=Depends(get_current_user)):
    owned(db,claim_id,user); v=db.query(Verification).filter(Verification.claim_id==claim_id).first()
    if not v: raise HTTPException(404,"Verification not found")
    return {"id":v.id,"claim_id":v.claim_id,"status":v.status,"confidence":v.confidence,"explanation":v.explanation,"sources":parse_sources(v.source),"created_at":v.created_at}
