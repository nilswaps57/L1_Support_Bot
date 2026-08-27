# Local Development Setup

## Prerequisites

Mandatory for local UI and backend development:

- Python 3.11 or newer
- uv
- Node.js 20 or newer
- npm

Optional for live ingestion and answering:

- Qdrant standalone binary, or the temporary Docker command below
- Ollama
- An approved embedding provider or local Ollama embedding model
- Oracle test connectivity; SQLite remains the default local database

Qdrant, Ollama, Oracle, and external embedding services are introduced by later phases.
SQLite is the default local relational database. Containers and CI/CD are intentionally
out of scope.

## Install Dependencies

```bash
cd /home/labuser/Desktop/L1_Support_Bot
unset VIRTUAL_ENV

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

Run backend commands with `uv run` from `backend/`. The `unset VIRTUAL_ENV` step prevents
an unrelated active virtual environment from causing uv's environment-mismatch warning;
`uv run` then uses the project environment created by `uv sync`. Run frontend commands from
`frontend/` with the project-local npm installation.

## Environment Variables

The safe templates are `backend/.env.example` and `frontend/.env.example`. The backend
settings below are optional unless a live service is being used:

| Variable | Default or safe placeholder | Purpose |
|---|---|---|
| `DATABASE_URL` | `sqlite+aiosqlite:///./dev.db` | Relational metadata and job state |
| `QDRANT_URL` | `http://localhost:6333` | Vector search service |
| `FILE_STORAGE_PATH` | `./data/documents` | UUID-backed source-file storage |
| `EMBEDDING_BASE_URL` | `http://localhost:11434/v1` | OpenAI-compatible embedding endpoint |
| `EMBEDDING_MODEL` | `nomic-embed-text` | Embedding model identity |
| `OLLAMA_BASE_URL` | `http://localhost:11434` | Local LLM endpoint |
| `OLLAMA_MODEL` | `phi3.5` | Development LLM identity |
| `CORS_ALLOWED_ORIGINS` | `http://localhost:5173` | Explicit local frontend origin |
| `MAX_DOCUMENT_SIZE_BYTES` | `10485760` | Upload size limit |

Do not add API keys, passwords, Oracle credentials, real endpoints, or licensed document
content to templates, logs, tests, or source control.

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

For temporary local development only, Qdrant can also be run with Docker:

```bash
docker run --rm --name l1-support-bot-qdrant -p 6333:6333 qdrant/qdrant
```

This is not the deployment architecture and is not required by the project plan. Stop it
with `docker stop l1-support-bot-qdrant` when finished.

Start Ollama separately when live generation is approved:

```bash
ollama serve
ollama pull nomic-embed-text
ollama pull phi3.5
```

An external embedding provider is optional and must be approved before any document or query
data leaves controlled infrastructure. Set `EMBEDDING_BASE_URL`, `EMBEDDING_MODEL`, and any
provider secret through the local environment only.

The live Docling validation command accepts a representative document or directory:

```bash
cd backend
uv run python scripts/validate_docling.py /path/to/flexcube-manual-subset
```

The command reports `blocked` when no representative PDF, DOCX, or Markdown input is supplied.

## Phase 15 Readiness Checks

Run the local checks from the repository root or the directory shown:

```bash
cd backend
uv lock --check
uv run alembic upgrade head
uv run alembic current
uv run alembic heads
uv run pytest tests/unit tests/api tests/integration -q
uv run ruff check .
uv run mypy src/l1_support_bot --strict
uv run tach check

cd ../frontend
npm run test:run
npm run build
npm run test:e2e:list
```

Opt-in live checks require locally approved services and data:

- Qdrant: start the standalone binary and run the Qdrant integration tests.
- Ollama: start `ollama serve`, pull an approved embedding/LLM model, and run live chat tests.
- Embeddings: provide an approved endpoint and the evaluated model configuration.
- Oracle: provide a safe test database; do not use production credentials or data.
- FLEXCUBE document: store the approved PDF outside tracked paths in a Git-ignored directory.

Docker-based Qdrant is not required and remains a temporary local-development alternative only
while deployment topology is undecided. Authentication and Configuration-area authorization are
not implemented and block real production deployment.

Phase 15 evaluation commands do not write source text or secrets to the repository:

```bash
cd backend
uv run python scripts/validate_docling.py /ignored/local/path/manual.pdf
uv run python scripts/evaluate_embeddings.py /ignored/local/path/fixture.json candidates.json
```

The commands return a blocked result when required reviewed fixtures or endpoints are absent.

## Operating Workflows

Apply migrations before starting the backend:

```bash
cd /home/labuser/Desktop/L1_Support_Bot
unset VIRTUAL_ENV
cd backend
uv run alembic upgrade head
uv run uvicorn l1_support_bot.interface.api.main:app --reload --port 8000
```

Start the asynchronous ingestion worker in a second terminal:

```bash
cd /home/labuser/Desktop/L1_Support_Bot
unset VIRTUAL_ENV
cd backend
uv run python -m l1_support_bot.worker.runner
```

Upload a PDF, DOCX, or Markdown file through the Configuration UI or API. Monitor the
document list and job endpoint for `QUEUED`, parsing/chunking, embedding/indexing, and the
terminal `COMPLETED`, `COMPLETED_WITH_WARNING`, or `FAILED` state. A source file is stored
under `FILE_STORAGE_PATH` using a UUID-based path; the original filename is display metadata.

Use the Chat route after a document is indexed. Supported answers show validated citations;
insufficient-information responses show no citations. Feedback is supervised data only and
does not automatically change prompts, models, retrieval, or documents.

Re-indexing creates a replacement index before cutover. Deletion removes the document and
its indexed chunks after confirmation; deletion during active ingestion is rejected with
`DOCUMENT_IN_PROCESSING` and can be retried after a terminal state.

The Configuration area exposes non-secret LLM, embedding, retrieval, and chunking settings.
Embedding or chunking changes can require explicit re-index confirmation. If the relational
database is unavailable, the UI enters explicit limited mode: indexed chat can remain usable
when its required vector, LLM, and cached configuration dependencies are available, while
uploads, ingestion, feedback, and configuration mutations are disabled.

Oracle connectivity is optional for local development. Use a dedicated safe test database and
never production credentials or data. Set `DATABASE_URL` only in the ignored local `.env`.

## Testing and Troubleshooting

Backend checks run from `backend/` with `uv run`; frontend checks run from `frontend/`:

```bash
cd backend
unset VIRTUAL_ENV
uv run pytest -q
uv run ruff check .
uv run mypy src/l1_support_bot --strict
uv run tach check

cd ../frontend
npm run test:run
npm run build
npm run test:e2e:list
```

For browser tests, start `npm run dev` in `frontend/` and use the focused or full Playwright
command documented by the task being validated. The committed E2E fixtures are deterministic;
live outage checks and model evaluations require separately approved services and data.

Common issues:

- If uv reports an environment mismatch, run `unset VIRTUAL_ENV`, then repeat the command from
	`backend/` with `uv run`.
- If the frontend cannot reach the backend, confirm port 8000, the local API origin, and the
	CORS origin in the ignored environment file.
- If documents stay queued, confirm the worker is running and that migrations completed.
- If indexing fails, verify Qdrant and the embedding endpoint; inspect only sanitized job
	diagnostics, not source text or credentials.
- If chat is unavailable, verify the vector store and Ollama/provider health separately.

Stop local processes with `Ctrl+C`. Stop Ollama with `Ctrl+C` in its serving terminal, stop
the standalone Qdrant process with `Ctrl+C`, and stop the temporary Docker Qdrant container
with the command above. Do not remove the local database or storage directory while jobs are
active; stop the worker first.

Real FLEXCUBE documents, live model/provider measurements, reviewer adjudication, and final
embedding/LLM selection remain deferred. No result should be recorded from synthetic fixtures
as though it were a production-quality result.
