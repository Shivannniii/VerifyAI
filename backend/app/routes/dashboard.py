from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session
from app.database import get_db
from app.dependencies import get_current_user
from app.models.research import ResearchPaper
from app.models.claim import Claim
from app.models.verification import Verification
from app.models.detector import DetectorAnalysis
from app.models.user import User

router=APIRouter(prefix="/dashboard",tags=["Dashboard"])
@router.get("/stats")
def stats(db:Session=Depends(get_db),user:User=Depends(get_current_user)):
    papers=db.query(func.count(ResearchPaper.id)).filter(ResearchPaper.user_id==user.id).scalar() or 0
    claims=db.query(func.count(Claim.id)).join(ResearchPaper,Claim.research_id==ResearchPaper.id).filter(ResearchPaper.user_id==user.id).scalar() or 0
    checked=db.query(func.count(Verification.id)).join(Claim,Verification.claim_id==Claim.id).join(ResearchPaper,Claim.research_id==ResearchPaper.id).filter(ResearchPaper.user_id==user.id,Verification.status!="unverified").scalar() or 0
    supported=db.query(func.count(Verification.id)).join(Claim,Verification.claim_id==Claim.id).join(ResearchPaper,Claim.research_id==ResearchPaper.id).filter(ResearchPaper.user_id==user.id,Verification.status.in_(["supported","potentially_supported"])).scalar() or 0
    contradicted=db.query(func.count(Verification.id)).join(Claim,Verification.claim_id==Claim.id).join(ResearchPaper,Claim.research_id==ResearchPaper.id).filter(ResearchPaper.user_id==user.id,Verification.status=="contradicted").scalar() or 0
    partial=db.query(func.count(Verification.id)).join(Claim,Verification.claim_id==Claim.id).join(ResearchPaper,Claim.research_id==ResearchPaper.id).filter(ResearchPaper.user_id==user.id,Verification.status=="partially_supported").scalar() or 0
    insufficient=db.query(func.count(Verification.id)).join(Claim,Verification.claim_id==Claim.id).join(ResearchPaper,Claim.research_id==ResearchPaper.id).filter(ResearchPaper.user_id==user.id,Verification.status.in_(["insufficient_evidence","uncertain"])).scalar() or 0
    detector=db.query(func.count(DetectorAnalysis.id)).filter(DetectorAnalysis.user_id==user.id).scalar() or 0
    return {"papers":papers,"claims":claims,"checked":checked,"supported":supported,"contradicted":contradicted,"partial":partial,"insufficient":insufficient,"detector_analyses":detector,"verification_rate":round(checked/claims*100) if claims else 0}
