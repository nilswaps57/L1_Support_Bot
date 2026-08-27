# Local Development Setup

## Prerequisites

- Python 3.11 or newer
- uv
- Node.js 20 or newer
- npm

Qdrant, Ollama, Oracle, and external embedding services are introduced by later phases.
SQLite is the default local relational database. Containers and CI/CD are intentionally
out of scope.

## Install Dependencies

```bash
cd backend
uv sync

cd ../frontend
npm install
```

Copy the example environment files before running a configured application:

```bash
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env.local
```

Do not place credentials in either example file or commit local environment files.

## Direct Startup

Run the backend from `backend/` after the FastAPI application factory is available:

```bash
uv run uvicorn l1_support_bot.interface.api.main:app --reload --port 8000
```

Run the frontend from `frontend/`:

```bash
npm run dev
```

The default frontend URL is `http://localhost:5173` and the default backend URL is
`http://localhost:8000`.

## Phase 3 Document Management

Phase 3 uses SQLite for the local document registry and ingestion-job queue, plus a local
filesystem directory for source files. From `backend/`, apply the migration before starting
the API:

```bash
cd backend
cp .env.example .env
uv run alembic upgrade head
uv run uvicorn l1_support_bot.interface.api.main:app --reload --port 8000
```

The default settings use `sqlite+aiosqlite:///./dev.db` and `./data/documents`. The storage
adapter never uses the uploaded filename as a path; it writes a UUID-based filename and
verifies the SHA-256 checksum. Keep the storage directory outside source control.

The document API can be smoke-tested after startup:

```bash
curl -X POST http://localhost:8000/api/v1/documents/upload \
	-F "file=@sample.pdf" -F "source_type=flexcube_manual"
curl http://localhost:8000/api/v1/documents
curl http://localhost:8000/api/v1/documents/{document_id}
```

Accepted uploads return `202` with `QUEUED` status. Phase 3 registers the source and creates
the job; document parsing, chunking, embeddings, vector indexing, and chatbot behavior are
intentionally introduced by later phases.

## Phase 1 Checks

```bash
cd backend
uv run ruff check .
uv run mypy src/l1_support_bot --strict
uv run pytest
uv run tach check

cd ../frontend
npm run test:run
npm run build
npm run test:e2e:list
```

These checks validate the project foundation and test discovery. Feature behavior is added
and validated in later phases.

## Phase 5 local services

The Phase 5 adapters use a standalone Qdrant binary and an Ollama process; Docker is not
required. Start Qdrant with its downloaded Linux binary and Ollama with `ollama serve` when
running live vector or generation checks. Automated tests use deterministic fakes or Qdrant's
in-memory client and do not require either service.

The live Docling validation command accepts a representative document or directory:

```bash
cd backend
uv run python scripts/validate_docling.py /path/to/flexcube-manual-subset
```

The command reports `blocked` when no representative PDF, DOCX, or Markdown input is supplied.
