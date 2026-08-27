# Quickstart Validation

**Validation date:** 2026-08-27
**Environment:** Linux, Python 3.14 project virtual environment, Node.js 22.22.2, npm, uv
**Reproducibility:** This was a repository-local validation using existing dependency caches and
already available local services. It is not a clean-machine reproducibility certification.

## Environment and dependency checks

Executed successfully:

- `unset VIRTUAL_ENV; uv lock --check`; uv used the backend project environment without the
  previously observed environment-mismatch warning.
- `npm install` using the existing frontend lockfile.
- `npm run test:run` and `npm run build` from `frontend/`.
- `uv run alembic upgrade head`, `current`, and `heads` against the local SQLite setup.
- Disposable SQLite upgrade, current, heads, downgrade-to-base, and upgrade-to-head checks.
- Project-local imports for the FastAPI application and
  `l1_support_bot.worker.runner` through `uv run`.

Mandatory local dependencies are Python/uv, Node.js/npm, and SQLite. Qdrant, Ollama, an
embedding provider, Oracle, and an approved FLEXCUBE document are optional prerequisites for
live ingestion or answering checks.

## Startup and operating checks

- Backend startup command is documented as `uv run uvicorn
  l1_support_bot.interface.api.main:app --reload --port 8000` from `backend/`.
- The backend started successfully on an isolated port with the project-local Uvicorn
  dependency. Its health endpoint returned HTTP 200 with `status=degraded` and
  `database=unavailable`; this disposable run did not establish a healthy seeded runtime
  configuration, so no healthy-backend claim is made.
- Worker startup command is documented and import-validated as `uv run python -m
  l1_support_bot.worker.runner`. A long-running worker was not left running after validation.
- Frontend startup was exercised with `npm run dev -- --host localhost`; browser tests used a
  local Vite process. Port 5173 was already occupied during one run, so Vite used port 5174.
- Qdrant health was reachable from the local environment. No licensed document was indexed.
- Ollama was reachable and reported only the local development inventory
  `qwen2.5:0.5b` and `nomic-embed-text`. The development embedding endpoint was therefore
  available, but no production model conclusion was drawn.
- Oracle was not configured. SQLite was used for local metadata and migration checks.

## Feature validation

The deterministic frontend E2E fixtures validated upload acknowledgement, asynchronous status
progress, indexed status, grounded response presentation, separate citations, feedback,
re-index/delete UI paths, configuration views, and degraded-mode presentation. The full
backend API/integration regression suite for the relevant flows also passed.

The following could not be validated against the real backend pipeline because no approved
FLEXCUBE document is present:

- Real PDF/DOCX/Markdown upload through live ingestion
- Docling parsing and large-document behavior on licensed content
- Real embedding and Qdrant indexing
- Grounded live chat and citation traceability against a FLEXCUBE source
- Live feedback, re-index, and deletion against persisted production-like data

Those gaps keep T085 open. Deterministic fixtures are not presented as real-document evidence.

## Deviations, warnings, and workarounds

- Existing dependency caches and services were reused; no clean-machine claim is made.
- The first frontend test attempt used unsupported Vitest flag `--runInBand`; the project
  command `npm run test:run` was used successfully afterward.
- Python 3.14 emits `pytest-asyncio` event-loop-policy deprecation warnings. They do not fail
  tests and should be resolved when the plugin supports the newer runtime.
- FastAPI/Starlette emits an `httpx` TestClient deprecation warning. Dependency changes were not
  applied automatically.
- Tach validates the configured module graph but emits its source-root warning because it does
  not detect first-party imports. The declared `source_roots = ["src"]` and module boundaries
  remain intact; the warning was recorded rather than weakening the architecture check.
- `pip-audit` is unavailable, so backend vulnerability certification remains open.
- No Oracle credentials, real endpoints, licensed documents, generated answers, vector data,
  databases, or model artifacts are stored in this report or repository.

## Safe shutdown

The temporary Vite process started for browser validation was stopped. The process already using
port 5173 was not terminated. Long-running backend, worker, Qdrant, and Ollama processes should
be stopped with `Ctrl+C` in their owning terminal; a temporary Docker Qdrant container should
be stopped with `docker stop l1-support-bot-qdrant`. Stop the worker before removing local
database or file-storage data.

## Deferred evidence

T133/T134 reranking, T209 embedding selection, T210 LLM selection, human adversarial review,
live outage/recovery validation, vulnerability certification, and full accessibility
certification remain open. No production-readiness or clean-machine reproducibility claim is
made by this validation.
