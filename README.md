# VerifyAI — Final Full-Stack Build

VerifyAI is an evidence-first research verification and AI-content screening application.

## Stack
- Frontend: React + Vite
- Backend: FastAPI + SQLAlchemy + SQLite
- Scholarly retrieval: OpenAlex
- Optional LLM: Gemini API, server-side only

## Run backend
```powershell
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
# copy .env.example to .env and add GEMINI_API_KEY if desired
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

## Run frontend
```powershell
cd frontend
npm install
npm run dev
```

The frontend proxies `/api` to `http://127.0.0.1:8000`.

## LLM
Set `GEMINI_API_KEY` in `backend/.env`. The default is `gemini-2.5-flash-lite`. If no key is configured, VerifyAI still works using deterministic baseline claim extraction and evidence matching.

## Important
- Do not commit real `.env` files or API keys.
- The LLM is used to reason over retrieved evidence; it is not itself treated as evidence.
- Baseline detector results are screening signals, not proof of authorship.
