import json, os, re
from urllib.parse import quote
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

OPENALEX_URL="https://api.openalex.org/works"
OPENALEX_API_KEY=os.getenv("OPENALEX_API_KEY","").strip()
OPENALEX_EMAIL=os.getenv("OPENALEX_EMAIL","").strip()

class SourceSearchError(Exception): pass

def _request_json(url):
    headers={"User-Agent":"VerifyAI/2.0 research-verification"}
    if OPENALEX_EMAIL: headers["From"]=OPENALEX_EMAIL
    try:
        with urlopen(Request(url,headers=headers),timeout=20) as r: return json.loads(r.read().decode())
    except (HTTPError,URLError,TimeoutError) as exc: raise SourceSearchError(f"Scholarly source search failed: {exc}") from exc

def _clean_text(text): return re.sub(r"\s+"," ",re.sub(r"[^a-z0-9\s]"," ",(text or "").lower())).strip()

def _keywords(text):
    stop={"the","and","for","with","that","this","from","were","was","are","has","have","had","into","their","they","them","than","then","there","which","will","would","could","should","about","between","after","before","during","using","used","also","these","those","such","more","most","than"}
    return {w for w in _clean_text(text).split() if len(w)>=4 and w not in stop}

def _score(claim,evidence):
    a,b=_keywords(claim),_keywords(evidence)
    return round(len(a&b)/len(a),3) if a else 0.0

def _abstract(work):
    inv=work.get("abstract_inverted_index") or {}
    words=[]
    for word,positions in inv.items():
        for pos in positions: words.append((pos,word))
    words.sort(); return " ".join(w for _,w in words)

def search_sources(query,limit=5):
    safe=re.sub(r"[^a-zA-Z0-9\s.,;:%()\'\"-]", " ", (query or "")[:500])
    safe=re.sub(r"\s+"," ",safe).strip()
    if len(safe)<10: return []
    url=f"{OPENALEX_URL}?search={quote(safe)}&per_page={limit}"
    if OPENALEX_API_KEY: url += f"&api_key={quote(OPENALEX_API_KEY)}"
    data=_request_json(url)
    results=[]
    for work in data.get("results",[]):
        loc=work.get("primary_location") or {}; source=loc.get("source") or {}
        abstract=_abstract(work)
        results.append({"id":work.get("id"),"title":work.get("title") or "Untitled source","url":work.get("doi") or work.get("id"),"snippet":abstract[:1800],"source_type":"academic","publication_year":work.get("publication_year"),"cited_by_count":work.get("cited_by_count",0),"source_name":source.get("display_name")})
    return results

def rank_sources(claim,sources):
    ranked=[]
    for s in sources:
        evidence=" ".join([s.get("title") or "",s.get("snippet") or "",s.get("source_name") or ""])
        x=dict(s); x["relevance"]=_score(claim,evidence); ranked.append(x)
    return sorted(ranked,key=lambda x:(x.get("relevance",0),x.get("cited_by_count",0)),reverse=True)

def verify_claim_with_sources(claim):
    from app.services.gemini_service import enabled, verify_claim as llm_verify
    sources=rank_sources(claim,search_sources(claim,5))
    evidence=[s for s in sources if s.get("relevance",0)>=0.12][:5]
    if enabled() and evidence:
        result=llm_verify(claim,evidence)
        selected=[evidence[i] for i in result.get("evidence_ids",[]) if isinstance(i,int) and 0<=i<len(evidence)]
        return {"verdict":{"SUPPORTS":"supported","CONTRADICTS":"contradicted","INSUFFICIENT_EVIDENCE":"insufficient_evidence"}.get(result["verdict"],"insufficient_evidence"),"confidence":result["confidence"],"explanation":result["explanation"],"sources":selected or evidence[:3],"mode":"gemini"}
    if not evidence:
        return {"verdict":"insufficient_evidence","confidence":0.2,"explanation":"No sufficiently relevant scholarly evidence was found. This is an evidence-availability result, not proof that the claim is false.","sources":[],"mode":"baseline"}
    best=evidence[0]["relevance"]
    if best>=0.7: verdict="potentially_supported"; conf=min(.95,.55+best*.4); explanation="Strong lexical relevance was found in scholarly records. Without an LLM evidence judgment, this is only a candidate support signal."
    elif best>=0.45: verdict="partially_supported"; conf=.45+best*.25; explanation="Relevant scholarly records were found, but the baseline matcher cannot establish whether they support or contradict the full claim."
    else: verdict="uncertain"; conf=.3+best*.2; explanation="Some topical overlap was found, but evidence relevance is too weak for a strong verdict."
    return {"verdict":verdict,"confidence":round(conf,2),"explanation":explanation,"sources":evidence[:5],"mode":"baseline"}
