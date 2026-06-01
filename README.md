# SmartDoc AI

SmartDoc AI converts static documents into searchable, summarized, and source-attributed insights. It pairs a FastAPI + Python backend (document parsing and AI orchestration) with an Angular frontend for a modern interactive experience.

## Key highlights
- Tech: Python (FastAPI) backend, Angular 16 frontend
- Document formats: PDF, DOCX, RTF, XLSX
- AI: Pluggable provider (OpenAI/Groq/Gemini) via BYOK (.env)

## Summary
SmartDoc AI extracts text from documents, generates source-cited summaries, produces five executive takeaways, and answers document-specific questions. It is stateless by design: document contents are kept in memory for each analysis session and are not persisted.

## Features
- Parse and extract text from PDF, DOCX, RTF and XLSX files
- Generate source-cited summaries and extract 5 executive takeaways
- Context-aware Q&A restricted to the provided document text
- Minimal architecture — no external document indexing or long-term storage

## Architecture Overview
- Frontend: Angular 16 app (serves UI and calls backend endpoints)
- Backend: FastAPI service exposing endpoints for upload, summarize, and Q&A
- AI: Backend calls a configured AI provider using an API key from `.env`

## Requirements
- Python 3.12+
- Node.js 16+ and npm
- Recommended: create a Python virtual environment for the backend

## Quick start — Backend
1. Open a terminal and create+activate a virtual environment (recommended):

```bash
cd backend
python -m venv .venv
# Windows
.\.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate
```

2. Install dependencies and create `.env`:

```bash
pip install -r requirements.txt
copy ..\.env.sample .env  # or create .env manually
```

3. Edit `backend/.env` and set `AI_PROVIDER_KEY` (DO NOT commit this file):

```
AI_PROVIDER_URL=https://api.groq.com/openai/v1/chat/completions
AI_PROVIDER_MODEL=llama-3.1-8b-instant
AI_PROVIDER_KEY=YOUR_API_KEY_HERE
DATABASE_URL=sqlite:///./doc_analyzer.db
```

4. Run the backend (development):

```bash
python main.py
# or using uvicorn
uvicorn main:app --reload --host 0.0.0.0 --port 8081
```

The backend exposes a health endpoint at `http://127.0.0.1:8081/api/documents/test`.

## Quick start — Frontend
1. Install dependencies and start the Angular dev server:

```bash
cd frontend
npm install
npm start
```

2. Open the app at `http://localhost:4200` (default Angular port).

## Configuration
- All runtime secrets and provider settings are stored in `backend/.env`. Keep it out of source control.
- The repo includes `backend/.env` currently for local convenience; replace values before deploying and ensure `.gitignore` prevents committing secrets.

## API Endpoints (summary)
- POST `/api/documents/analyze` — multipart upload: `file` (+ optional `tone`) → returns `extractedText`, `summary`, `takeaways`
- POST `/api/documents/ask` — JSON: `{ "text": "...", "question": "..." }` → returns `{ "answer": "..." }`
- POST `/api/documents/summarize` — JSON `{ "text": "...", "tone": "executive" }` → returns `{ "summary": ..., "takeaways": [...] }`
- GET `/api/documents/test` — health check

Example curl (analyze):

```bash
curl -X POST "http://127.0.0.1:8081/api/documents/analyze" \
  -F "file=@/path/to/document.pdf" \
  -F "tone=executive"
```

## Security & Privacy
- API keys: keep `AI_PROVIDER_KEY` private. Never commit `.env` to Git. Use environment secrets in CI/CD.
- Document data: this project is intentionally stateless; documents only live in memory during processing.


