from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from app.database import get_db
from app.dependencies import get_current_user
from app.models.detector import DetectorAnalysis
from app.models.user import User
from app.services.detector_service import analyze_text
from app.services.pdf_service import extract_text_from_pdf

router=APIRouter(prefix="/detector",tags=["AI Detector"])
class DetectorRequest(BaseModel): text:str=Field(min_length=20,max_length=100000)

def serialize(x): return {"id":x.id,"input_type":x.input_type,"filename":x.filename,"word_count":x.word_count,"sentence_count":x.sentence_count,"ai_probability":x.ai_probability,"human_probability":x.human_probability,"confidence":x.confidence,"classification":x.classification,"mode":x.mode,"explanation":x.explanation,"created_at":x.created_at}

def save(db,user,text,input_type="text",filename=None):
    r=analyze_text(text); x=DetectorAnalysis(user_id=user.id,input_type=input_type,filename=filename,text=text,**r); db.add(x); db.commit(); db.refresh(x); return serialize(x)

@router.post("/analyze")
def analyze(body:DetectorRequest,db:Session=Depends(get_db),user:User=Depends(get_current_user)): return save(db,user,body.text,"text")

@router.post("/analyze-file")
async def analyze_file(file:UploadFile=File(...),db:Session=Depends(get_db),user:User=Depends(get_current_user)):
    if not file.filename or not file.filename.lower().endswith((".pdf",".txt")): raise HTTPException(400,"Only PDF and TXT files are supported")
    data=await file.read(20*1024*1024+1)
    if len(data)>20*1024*1024: raise HTTPException(413,"File is too large (maximum is 20 MB)")
    if file.filename.lower().endswith(".pdf"):
        try: text=extract_text_from_pdf(data)
        except ValueError as e: raise HTTPException(400,str(e))
    else: text=data.decode("utf-8",errors="ignore")
    if len(text.strip())<20: raise HTTPException(422,"Not enough readable text for analysis")
    return save(db,user,text,"file",file.filename[:255])

@router.get("/history")
def history(db:Session=Depends(get_db),user:User=Depends(get_current_user)):
    return [serialize(x) for x in db.query(DetectorAnalysis).filter(DetectorAnalysis.user_id==user.id).order_by(DetectorAnalysis.created_at.desc()).limit(50).all()]

@router.get("/{analysis_id}")
def get_analysis(analysis_id:int,db:Session=Depends(get_db),user:User=Depends(get_current_user)):
    x=db.query(DetectorAnalysis).filter(DetectorAnalysis.id==analysis_id,DetectorAnalysis.user_id==user.id).first()
    if not x: raise HTTPException(404,"Detector analysis not found")
    return serialize(x)
