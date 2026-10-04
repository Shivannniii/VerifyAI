import os
import uuid
from pathlib import Path

from fastapi import (
    APIRouter,
    Depends,
    File,
    HTTPException,
    UploadFile,
    status,
)
from pydantic import BaseModel, Field
from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload

from app.database import BASE_DIR, get_db
from app.dependencies import get_current_user
from app.models.claim import Claim
from app.models.research import ResearchPaper
from app.models.user import User
from app.serializers import VERIFIED_STATUSES, serialize_claim
from app.services.analysis_service import analyze_research
from app.services.pdf_service import extract_text_from_pdf


router = APIRouter(
    prefix="/research",
    tags=["Research"]
)

UPLOAD_DIR = BASE_DIR / "uploads"
MAX_UPLOAD_BYTES = 20 * 1024 * 1024  # 20 MB


# =========================================================
# HELPERS
# =========================================================

def get_owned_paper(
    db: Session,
    research_id: int,
    user: User,
) -> ResearchPaper:
    """Return the paper only if it belongs to the logged-in user."""

    paper = (
        db.query(ResearchPaper)
        .filter(
            ResearchPaper.id == research_id,
            ResearchPaper.user_id == user.id,
        )
        .first()
    )

    if not paper:
        raise HTTPException(
            status_code=404,
            detail="Research paper not found"
        )

    return paper


def serialize_paper(paper: ResearchPaper, **extra) -> dict:
    text = paper.extracted_text or ""

    return {
        "id": paper.id,
        "filename": paper.filename,
        "status": paper.status,
        "created_at": paper.created_at,
        "text_length": len(text),
        "text_preview": text[:2000],
        **extra,
    }


# =========================================================
# LIST MY PAPERS
# =========================================================

@router.get("")
def list_research(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    papers = (
        db.query(ResearchPaper)
        .filter(ResearchPaper.user_id == current_user.id)
        .order_by(
            ResearchPaper.created_at.desc(),
            ResearchPaper.id.desc(),
        )
        .all()
    )

    ids = [paper.id for paper in papers]

    claim_counts = {}
    verified_counts = {}

    if ids:
        claim_counts = dict(
            db.query(Claim.research_id, func.count(Claim.id))
            .filter(Claim.research_id.in_(ids))
            .group_by(Claim.research_id)
            .all()
        )

        verified_counts = dict(
            db.query(Claim.research_id, func.count(Claim.id))
            .filter(
                Claim.research_id.in_(ids),
                Claim.status.in_(VERIFIED_STATUSES),
            )
            .group_by(Claim.research_id)
            .all()
        )

    return [
        {
            "id": paper.id,
            "filename": paper.filename,
            "status": paper.status,
            "created_at": paper.created_at,
            "claim_count": claim_counts.get(paper.id, 0),
            "verified_count": verified_counts.get(paper.id, 0),
        }
        for paper in papers
    ]


# =========================================================
# PDF UPLOAD
# =========================================================

@router.post("/upload", status_code=status.HTTP_201_CREATED)
async def upload_research(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Upload a PDF, extract its text and create a database record
    owned by the logged-in user.
    """

    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided")

    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are supported"
        )

    contents = await file.read(MAX_UPLOAD_BYTES + 1)

    if not contents:
        raise HTTPException(status_code=400, detail="Uploaded file is empty")

    if len(contents) > MAX_UPLOAD_BYTES:
        raise HTTPException(
            status_code=413,
            detail="File is too large (maximum is 20 MB)"
        )

    if not contents.startswith(b"%PDF-"):
        raise HTTPException(
            status_code=400,
            detail="The file does not look like a valid PDF"
        )

    try:
        extracted_text = extract_text_from_pdf(contents)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))

    if not extracted_text.strip():
        raise HTTPException(
            status_code=422,
            detail=(
                "No selectable text was found in this PDF. "
                "It may be a scanned image - please upload a text-based PDF."
            )
        )

    # Never trust the client's filename for the path on disk
    # (it allowed overwrites and path tricks like "..\\x.pdf").
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    stored_name = f"{uuid.uuid4().hex}.pdf"
    file_path = UPLOAD_DIR / stored_name

    try:
        file_path.write_bytes(contents)

        research = ResearchPaper(
            user_id=current_user.id,
            filename=os.path.basename(file.filename)[:255],
            file_path=f"uploads/{stored_name}",
            extracted_text=extracted_text,
            status="uploaded"
        )

        db.add(research)
        db.commit()
        db.refresh(research)

    except Exception as error:
        db.rollback()
        file_path.unlink(missing_ok=True)

        raise HTTPException(
            status_code=500,
            detail=f"Upload failed: {error}"
        )

    return {
        "message": "Research paper uploaded successfully.",
        "research_id": research.id,
        **serialize_paper(research),
    }


# =========================================================
# PASTE TEXT (e.g. an AI answer you want to fact-check)
# =========================================================

class TextSubmission(BaseModel):
    text: str = Field(min_length=80, max_length=100_000)
    title: str | None = Field(default=None, max_length=200)


@router.post("/text", status_code=status.HTTP_201_CREATED)
def submit_text(
    body: TextSubmission,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    text = body.text.strip()

    if len(text) < 80:
        raise HTTPException(
            status_code=400,
            detail="Please paste at least a couple of full sentences."
        )

    title = (body.title or "").strip() or f"Pasted text: {text[:40]}..."

    research = ResearchPaper(
        user_id=current_user.id,
        filename=title[:255],
        file_path=None,
        extracted_text=text,
        status="uploaded"
    )

    db.add(research)
    db.commit()
    db.refresh(research)

    return {
        "message": "Text saved successfully.",
        "research_id": research.id,
        **serialize_paper(research),
    }


# =========================================================
# GET ONE PAPER
# =========================================================

@router.get("/{research_id}")
def get_research(
    research_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    research = get_owned_paper(db, research_id, current_user)

    return serialize_paper(research)


# =========================================================
# GET CLAIMS (with their verification results)
# =========================================================

@router.get("/{research_id}/claims")
def get_research_claims(
    research_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    get_owned_paper(db, research_id, current_user)

    claims = (
        db.query(Claim)
        .options(joinedload(Claim.verification))
        .filter(Claim.research_id == research_id)
        .order_by(Claim.id)
        .all()
    )

    return [serialize_claim(claim) for claim in claims]


# =========================================================
# ANALYZE (extract claims)
# =========================================================

@router.post("/{research_id}/analyze")
def analyze_research_paper(
    research_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    research = get_owned_paper(db, research_id, current_user)

    if not research.extracted_text:
        raise HTTPException(
            status_code=400,
            detail="Research paper has no extracted text"
        )

    try:
        results = analyze_research(db, research)
    except Exception as error:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(error))

    return {
        "message": "Research analysis completed",
        "research_id": research.id,
        "filename": research.filename,
        "status": research.status,
        "claim_count": len(results),
        "claims": [serialize_claim(item["claim"]) for item in results],
    }


# =========================================================
# DELETE
# =========================================================

@router.delete("/{research_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_research(
    research_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    research = get_owned_paper(db, research_id, current_user)

    stored_file = None

    if research.file_path:
        candidate = (BASE_DIR / research.file_path).resolve()

        # only ever delete files that live inside the uploads folder
        if UPLOAD_DIR.resolve() in candidate.parents:
            stored_file = candidate

    db.delete(research)  # cascades to claims and verifications
    db.commit()

    if stored_file is not None:
        stored_file.unlink(missing_ok=True)
