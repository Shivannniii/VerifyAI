import re
from sqlalchemy.orm import Session
from app.models.claim import Claim
from app.models.research import ResearchPaper
from app.models.verification import Verification

def clean_research_text(text):
    text=re.sub(r"\r\n?","\n",text or ""); text=re.sub(r"(\w)-\n(\w)",r"\1\2",text); text=re.sub(r"[ \t]+"," ",text); text=re.sub(r"https?://doi\.org/\S+","",text,flags=re.I)
    lines=text.split("\n")
    for i in range(len(lines)-1,-1,-1):
        if re.fullmatch(r"\s*(references|bibliography|reference list)\s*",lines[i],re.I) and i>len(lines)*.4: lines=lines[:i]; break
    for i,line in enumerate(lines[:max(10,int(len(lines)*.3))]):
        if re.fullmatch(r"\s*abstract\s*[:.\-]?\s*",line,re.I): lines=lines[i+1:]; break
    bad=[r"^received\s*:",r"^accepted\s*:",r"^published\s*(online)?\s*:",r"^vol\.?\s*:",r"^volume\s*:",r"^issue\s*:",r"^doi\s*:",r"^copyright",r"^©",r"^author\(s\)",r"^license"]
    return "\n".join(x.strip() for x in lines if x.strip() and not any(re.search(p,x.strip(),re.I) for p in bad))

def split_sentences(text): return [s.strip() for s in re.split(r"(?<=[.!?])\s+(?=[A-Z0-9])",re.sub(r"\s+"," ",(text or "").replace("\n"," ")).strip()) if s.strip()]

def looks_like_claim(s):
    if len(s)<80 or len(s)>800: return False
    low=s.lower()
    if re.search(r"\b10\.\d{4,9}/\S+",low) or re.search(r"\bvolume\s+\d+|\bissue\s+\d+",low): return False
    if re.match(r"^\s*(references|bibliography)\b",low): return False
    indicators=[" is "," are "," was "," were "," has "," have "," can "," may "," could ","shows","demonstrates","indicates","suggests","found","results","increases","decreases","improves","reduces","affects","enables","significant","associated","correlated","predict","algorithm","machine learning","artificial intelligence"]
    return sum(1 for x in indicators if x in low)>=1

def extract_claims(text,max_claims=30):
    claims=[]; seen=set()
    for s in split_sentences(clean_research_text(text)):
        s=re.sub(r"\[\d+(?:,\s*\d+)*\]","",re.sub(r"\s+"," ",s)).strip()
        if not looks_like_claim(s): continue
        key=s.lower()
        if key in seen: continue
        seen.add(key); claims.append(s)
        if len(claims)>=max_claims: break
    return claims

def analyze_research(db:Session,research:ResearchPaper,max_claims=30):
    from app.services.gemini_service import enabled, extract_claims as llm_extract
    old=db.query(Claim).filter(Claim.research_id==research.id).all()
    for c in old: db.query(Verification).filter(Verification.claim_id==c.id).delete(synchronize_session=False)
    db.query(Claim).filter(Claim.research_id==research.id).delete(synchronize_session=False); db.commit()
    claims_text=[]
    if enabled():
        try: claims_text=llm_extract(research.extracted_text or "",max_claims)
        except Exception: claims_text=[]
    if not claims_text: claims_text=extract_claims(research.extracted_text or "",max_claims)
    results=[]
    for text in claims_text:
        claim=Claim(research_id=research.id,claim_text=text,status="pending"); db.add(claim); db.flush()
        v=Verification(claim_id=claim.id,status="unverified",confidence=0.0,explanation="Claim extracted. Evidence verification is pending.",source=None); db.add(v); db.flush(); results.append({"claim":claim,"verification":v})
    research.status="analysis_complete"; db.commit()
    for x in results: db.refresh(x["claim"]); db.refresh(x["verification"])
    return results
