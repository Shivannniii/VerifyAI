from pathlib import Path
from dotenv import load_dotenv

# Load backend/.env before importing routers/services
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import Base, engine
from app.models import User, ResearchPaper, Claim, Verification, DetectorAnalysis
from app.routes.auth import router as auth_router
from app.routes.research import router as research_router
from app.routes.user import router as user_router
from app.routes.verification import router as verification_router
from app.routes.detector import router as detector_router
from app.routes.dashboard import router as dashboard_router
from app.routes.report import router as report_router

app=FastAPI(title="VerifyAI API",description="Evidence-first AI-content detection and research verification platform.",version="3.0.0")
Base.metadata.create_all(bind=engine)
origins=[x.strip() for x in os.getenv("CORS_ORIGINS","http://localhost:5173,http://127.0.0.1:5173,http://localhost:4173,http://127.0.0.1:4173").split(",") if x.strip()]
app.add_middleware(CORSMiddleware,allow_origins=origins,allow_credentials=True,allow_methods=["*"],allow_headers=["*"])
app.include_router(auth_router,prefix="/api"); app.include_router(research_router,prefix="/api"); app.include_router(user_router,prefix="/api"); app.include_router(verification_router,prefix="/api"); app.include_router(detector_router,prefix="/api"); app.include_router(dashboard_router,prefix="/api"); app.include_router(report_router,prefix="/api")
@app.get("/")
def root(): return {"message":"VerifyAI backend is running","version":"3.0.0","llm_enabled":bool(os.getenv("GEMINI_API_KEY"))}
@app.get("/api/health")
def health(): return {"status":"healthy","service":"VerifyAI API","version":"3.0.0","llm_enabled":bool(os.getenv("GEMINI_API_KEY"))}
