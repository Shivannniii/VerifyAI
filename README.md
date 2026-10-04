# VerifyAI

### Evidence-Grounded Research Verification & AI Content Analysis

VerifyAI is a full-stack research verification platform designed to help users understand whether claims are supported by scholarly evidence.

Instead of treating an LLM as the source of truth, VerifyAI follows an evidence-first workflow:

Research Text / PDF
        ↓
Text Cleaning
        ↓
Atomic Claim Extraction
        ↓
Scholarly Retrieval
        ↓
Evidence Ranking
        ↓
LLM Reasoning Over Evidence
        ↓
Verification Verdict
        ↓
Evidence + Explanation + Confidence

## Core Features

- User registration and authentication
- Research text submission
- PDF research upload
- Automatic claim extraction
- Scholarly evidence retrieval using OpenAlex
- Evidence ranking and source display
- Gemini-powered evidence reasoning
- Claim verification
- SUPPORTS / CONTRADICTS / INSUFFICIENT EVIDENCE reasoning
- AI-content detection
- Research dashboard
- Verification history
- Research reports
- SQLite development database
- React/Vite frontend
- FastAPI backend

## Architecture

### Frontend

- React
- Vite
- React Router
- Lucide Icons
- Custom responsive UI

### Backend

- FastAPI
- SQLAlchemy
- SQLite
- JWT authentication
- PyMuPDF
- OpenAlex
- Google Gemini API

### Verification Pipeline

1. User submits research text or PDF.
2. VerifyAI cleans and prepares the text.
3. The system extracts atomic, independently checkable claims.
4. OpenAlex is queried for relevant scholarly records.
5. Retrieved evidence is ranked for relevance.
6. Gemini reasons over the retrieved evidence.
7. Each claim receives a verification verdict.
8. VerifyAI displays the evidence, explanation, and confidence.

> **The LLM reasons over evidence. The LLM is not the evidence.**

## AI Detector

VerifyAI also includes a lightweight AI-content detection module.

The detector currently provides:

- AI probability
- Human probability
- Confidence
- Classification
- Explanation

The detector is intended as a screening signal and is not presented as a definitive authorship classifier.

## Project Structure

```text
VerifyAI/
│
├── backend/
│   ├── app/
│   │   ├── models/
│   │   ├── routes/
│   │   ├── services/
│   │   └── main.py
│   ├── requirements.txt
│   ├── .env.example
│   └── uploads/
│
├── frontend/
│   ├── src/
│   ├── package.json
│   └── ...
│
├── start_backend.bat
├── start_frontend.bat
├── start_verifyai.bat
├── .gitignore
└── README.md