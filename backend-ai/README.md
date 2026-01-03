# Backend AI - Document Assignment System

ระบบจำแนกและมอบหมายเอกสาร PDF อัตโนมัติด้วย AI

## Quick Start

```bash
# 1. Start pgvector database
cd ../pgvector-doc-ai
docker compose up -d

# 2. Install dependencies
uv sync

# 3. Configure environment
# Edit .env and add your GOOGLE_API_KEY

# 4. Run server
uv run uvicorn app.main:app --reload --port 8000
```

## API Endpoints

- `POST /api/v1/ingest` - Upload PDF
- `POST /api/v1/assign/{doc_id}` - Assign document
- `GET /api/v1/documents` - List documents
- `POST /api/v1/employees` - Add employee profile

## Tech Stack

- FastAPI
- Gemini (Embedding + LLM)
- PostgreSQL + pgvector
- Google Cloud Vision (OCR)
