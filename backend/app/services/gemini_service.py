import json
import os
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash-lite").strip()

class GeminiNotConfigured(Exception): pass
class GeminiError(Exception): pass

def enabled(): return bool(GEMINI_API_KEY)

def _call(prompt: str, schema: dict, timeout: int = 60):
    if not enabled(): raise GeminiNotConfigured("GEMINI_API_KEY is not configured")
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent"
    body = {"contents":[{"parts":[{"text":prompt}]}], "generationConfig":{"temperature":0.1,"responseMimeType":"application/json","responseSchema":schema}}
    req = Request(url, data=json.dumps(body).encode(), headers={"Content-Type":"application/json","x-goog-api-key":GEMINI_API_KEY}, method="POST")
    try:
        with urlopen(req, timeout=timeout) as response: raw=response.read().decode("utf-8")
    except HTTPError as exc:
        detail=exc.read().decode("utf-8",errors="ignore")
        raise GeminiError(f"Gemini API error {exc.code}: {detail[:500]}") from exc
    except URLError as exc: raise GeminiError(f"Could not reach Gemini API: {exc.reason}") from exc
    data=json.loads(raw)
    text=data.get("candidates", [{}])[0].get("content",{}).get("parts",[{}])[0].get("text")
    if not text: raise GeminiError("Gemini returned no text")
    try: return json.loads(text)
    except json.JSONDecodeError as exc: raise GeminiError("Gemini returned invalid JSON") from exc

def extract_claims(text: str, max_claims: int = 30):
    schema={"type":"OBJECT","properties":{"claims":{"type":"ARRAY","items":{"type":"STRING"}}},"required":["claims"]}
    prompt=f"""You are the claim extraction component of VerifyAI, a research verification system. Extract up to {max_claims} atomic, independently checkable factual claims from the research text below. Exclude titles, author metadata, citations, references, navigation text, questions, vague opinions, and duplicate claims. Preserve important numbers, comparisons, populations, methods, and conclusions. Each item must be one self-contained sentence. Return only the JSON schema.\n\nTEXT:\n{text[:90000]}"""
    result=_call(prompt,schema)
    claims=[]
    for c in result.get("claims",[]):
        c=str(c).strip()
        if 40 <= len(c) <= 1000 and c not in claims: claims.append(c)
    return claims[:max_claims]

def verify_claim(claim: str, evidence: list[dict]):
    schema={"type":"OBJECT","properties":{"verdict":{"type":"STRING","enum":["SUPPORTS","CONTRADICTS","INSUFFICIENT_EVIDENCE"]},"confidence":{"type":"NUMBER"},"explanation":{"type":"STRING"},"evidence_ids":{"type":"ARRAY","items":{"type":"INTEGER"}}},"required":["verdict","confidence","explanation","evidence_ids"]}
    compact=[]
    for i,s in enumerate(evidence): compact.append({"id":i,"title":s.get("title"),"year":s.get("publication_year"),"source":s.get("source_name"),"excerpt":(s.get("snippet") or "")[:1800]})
    prompt=f"""You are VerifyAI's evidence-grounded verification reasoner. The claim is NOT evidence. Judge only from the supplied scholarly evidence. Do not use outside knowledge. If evidence directly supports the claim, return SUPPORTS. If reliable supplied evidence directly conflicts with the claim, return CONTRADICTS. If evidence is absent, too weak, ambiguous, or only topically related, return INSUFFICIENT_EVIDENCE. Confidence must be between 0 and 1 and reflect evidence quality/relevance, not model certainty. Give a concise explanation and identify only supplied evidence IDs that materially support the verdict.\n\nCLAIM:\n{claim}\n\nEVIDENCE:\n{json.dumps(compact,ensure_ascii=False)}"""
    result=_call(prompt,schema)
    result["confidence"]=max(0,min(1,float(result.get("confidence",0))))
    result["evidence_ids"]=list(result.get("evidence_ids",[]))
    return result
