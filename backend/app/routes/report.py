import json
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from app.database import get_db
from app.dependencies import get_current_user
from app.models.research import ResearchPaper
from app.models.claim import Claim
from app.models.user import User
from app.serializers import serialize_claim, parse_sources

router=APIRouter(prefix="/research",tags=["Reports"])

def owned(db,id,user):
    p=db.query(ResearchPaper).filter(ResearchPaper.id==id,ResearchPaper.user_id==user.id).first()
    if not p: raise HTTPException(404,"Research paper not found")
    return p

def build(db,p):
    claims=db.query(Claim).options(joinedload(Claim.verification)).filter(Claim.research_id==p.id).order_by(Claim.id).all()
    counts={"supported":0,"potentially_supported":0,"partially_supported":0,"contradicted":0,"insufficient_evidence":0,"uncertain":0,"unverified":0,"verification_pending":0,"pending":0}
    for c in claims: counts[c.status]=counts.get(c.status,0)+1
    checked=sum(counts[k] for k in ["supported","potentially_supported","partially_supported","contradicted","insufficient_evidence","uncertain"])
    positive=counts["supported"]+counts["potentially_supported"]
    score=round(positive/checked*100) if checked else 0
    return {"research":{"id":p.id,"filename":p.filename,"status":p.status,"created_at":p.created_at},"summary":{"claim_count":len(claims),"checked":checked,"score":score,"counts":counts},"claims":[serialize_claim(c) for c in claims]}

@router.get("/{research_id}/report")
def report(research_id:int,db:Session=Depends(get_db),user:User=Depends(get_current_user)): return build(db,owned(db,research_id,user))

@router.get("/{research_id}/report/markdown")
def markdown(research_id:int,db:Session=Depends(get_db),user:User=Depends(get_current_user)):
    data=build(db,owned(db,research_id,user)); s=data["summary"]; lines=[f"# VerifyAI Report — {data['research']['filename']}","",f"**Verification score:** {s['score']}%",f"**Claims:** {s['claim_count']} | **Checked:** {s['checked']}","","## Claim results",""]
    for i,c in enumerate(data["claims"],1):
        v=c.get("verification") or {}; lines += [f"### Claim {i}",c["claim_text"],f"- Verdict: {v.get('status','unverified')}",f"- Confidence: {round((v.get('confidence') or 0)*100)}%",f"- Explanation: {v.get('explanation') or 'Pending'}","" ]
    from fastapi.responses import PlainTextResponse
    return PlainTextResponse("\n".join(lines),media_type="text/markdown")
