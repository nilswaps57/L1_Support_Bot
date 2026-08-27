---

description: "Incremental task list for the FLEXCUBE L1 Support Chatbot"
---

# Tasks: FLEXCUBE L1 Support Chatbot

**Input**: Design documents from `specs/002-flexcube-support-chatbot/`

**Prerequisites**: `plan.md`, `spec.md`, `research.md`, `data-model.md`, `contracts/`, and `quickstart.md`

**Feature**: `002-flexcube-support-chatbot`

**Constitution**: `.specify/memory/constitution.md` v1.0.0

**Tests**: Required by the feature specification and Constitution Principle XXXVII. Tests are
included for domain rules, adapters, APIs, frontend behavior, end-to-end flows, and RAG quality.

**Confirmed lifecycle decision**: Deletion is blocked while ingestion is active and returns
`DOCUMENT_IN_PROCESSING`. The active ingestion job continues unchanged. T013 records this
confirmed rule in the design artifacts before story implementation begins.

## Format

Every implementation task uses:

`- [ ] [TaskID] [P?] [Story?] Description with exact file path`

`[P]` means the task can run in parallel with other tasks in its phase because it touches a
different file set and has no dependency on incomplete work. Story labels map to `spec.md`.

---

## Phase 1: Setup — Engineering Foundation (Plan Phase 0)

**Purpose**: Establish the repository, Python backend, React frontend, tooling, and documentation
scaffolding. No user-story business behavior is implemented in this phase.

- [X] T001 Create the repository directories `backend/`, `frontend/`, `docs/adr/`, `docs/architecture/`, `docs/evaluation/`, and `data/` according to `specs/002-flexcube-support-chatbot/plan.md`.
- [X] T002 Initialize the Python 3.11+ backend project and dependency lockfile in `backend/pyproject.toml` using uv with FastAPI, Pydantic Settings, SQLAlchemy, Alembic, httpx, pytest, pytest-asyncio, pytest-cov, ruff, mypy, tach, and structlog dependencies.
- [X] T003 [P] Initialize the React and TypeScript Vite application in `frontend/package.json`, `frontend/vite.config.ts`, `frontend/tsconfig.json`, and `frontend/src/main.tsx` with `react-hook-form` and `@hookform/resolvers` for schema-validated forms; do not introduce Redux or Zustand.
- [X] T004 [P] Add backend formatting, linting, typing, test, and architecture-check configuration to `backend/pyproject.toml` and `backend/tach.toml`.
- [X] T005 [P] Add frontend test dependencies and configuration to `frontend/package.json`, `frontend/vitest.config.ts`, `frontend/playwright.config.ts`, and `frontend/src/test/setup.ts`.
- [X] T006 [P] Create the backend package skeleton with `__init__.py` files under `backend/src/l1_support_bot/domain/`, `backend/src/l1_support_bot/application/`, `backend/src/l1_support_bot/infrastructure/`, and `backend/src/l1_support_bot/interface/`.
- [X] T007 [P] Create the frontend feature skeleton under `frontend/src/app/`, `frontend/src/features/configuration/`, `frontend/src/features/chatbot/`, and `frontend/src/shared/`.
- [X] T008 [P] Add safe development configuration templates to `backend/.env.example`, `frontend/.env.example`, and root `.gitignore`; do not include credentials or real endpoints requiring secrets.
- [X] T009 [P] Create the initial local setup and architecture documentation index in `README.md`, `docs/architecture/README.md`, and `docs/adr/README.md`.
- [X] T010 Add the constitution compliance checklist for implementation reviews to `docs/architecture/constitution-compliance.md`, covering grounded answers, source citations, security, no autonomous actions, and dependency direction.
- [X] T011 Add the Phase 0 test command documentation and local prerequisites to `docs/development/local-setup.md`, including direct backend/frontend startup and explicitly excluding containers and CI/CD.
- [X] T012 Verify the setup phase with `backend/pyproject.toml` commands for `uv run ruff check`, `uv run mypy`, `uv run pytest`, `uv run tach check`, and `frontend/package.json` commands for Vitest and Playwright discovery.

---

## Phase 2: Foundational — Blocking Prerequisites (Plan Phase 0)

**Purpose**: Build the dependency-safe domain/application foundation before any user story
implementation begins. This phase blocks all story phases.

**Lifecycle decision recorded**: T013 documents the confirmed deletion rule before US1 tasks begin.

- [X] T013 Record the confirmed deletion-during-active-ingestion policy (block deletion and return `DOCUMENT_IN_PROCESSING`) only in `specs/002-flexcube-support-chatbot/research.md` and `specs/002-flexcube-support-chatbot/data-model.md`, removing unresolved alternatives; `spec.md` and `plan.md` already confirm that deletion is blocked during active ingestion.
- [X] T014 [P] Define framework-free document, ingestion, chunk, citation, answer, session, feedback, and configuration value objects in `backend/src/l1_support_bot/domain/models/`.
- [X] T015 [P] Define domain status enums and validated lifecycle transition rules in `backend/src/l1_support_bot/domain/models/ingestion.py` for `UPLOADED`, `QUEUED`, `PARSING`, `NORMALISING`, `CHUNKING`, `READY_FOR_INDEXING`, `READY_FOR_INDEXING_WITH_WARNING`, `EMBEDDING`, `INDEXING`, `COMPLETED`, `COMPLETED_WITH_WARNING`, `FAILED`, `DELETING`, and `DELETED`, keeping both ready-for-indexing states non-queryable.
- [X] T016 [P] Define domain exception types and safe error categories in `backend/src/l1_support_bot/domain/errors.py`, including validation, duplicate, processing, unavailable-service, insufficient-evidence, and incompatible-index errors.
- [X] T017 [P] Define all application-owned ports as protocols in `backend/src/l1_support_bot/domain/ports/`, including repositories, file storage, parser, chunker, embedding, vector store, retriever, reranker, LLM, job queue, session store, and runtime configuration cache.
- [X] T018 [P] Add domain unit tests for invariants, status transitions, non-queryable ready-for-indexing states, `COMPLETED_WITH_WARNING`, citation identity, answer types, and configuration validation in `backend/tests/unit/domain/`.
- [X] T019 Implement Pydantic Settings loading and environment validation in `backend/src/l1_support_bot/interface/config.py` without exposing secret values in logs or responses.
- [X] T020 Implement structured JSON logging and privacy-safe request context in `backend/src/l1_support_bot/interface/logging.py`, including request ID and correlation ID support.
- [X] T021 Implement the common API error DTO and exception translation handlers in `backend/src/l1_support_bot/interface/dto/errors.py` and `backend/src/l1_support_bot/interface/api/middleware/errors.py`.
- [X] T022 Implement request-ID middleware, bounded request body handling, and configurable CORS in `backend/src/l1_support_bot/interface/api/middleware/request_context.py` and `backend/src/l1_support_bot/interface/api/middleware/cors.py`.
- [X] T023 Implement the FastAPI application factory and versioned router registration in `backend/src/l1_support_bot/interface/api/main.py` and `backend/src/l1_support_bot/interface/api/routers/__init__.py`.
- [X] T024 [P] Implement dependency-injection wiring for ports and adapters in `backend/src/l1_support_bot/interface/dependencies.py`; keep concrete SDK imports out of domain and application packages.
- [X] T025 [P] Configure tach module boundaries in `backend/tach.toml` so Domain imports no framework/infrastructure, Application imports Domain only, Infrastructure implements Domain ports, and Interface invokes Application use cases.
- [X] T026 Add architecture boundary and import smoke tests in `backend/tests/unit/test_architecture_boundaries.py` and `backend/tests/api/test_app_startup.py`, including verification that the domain and application layers define no tool-execution port, arbitrary SQL-execution port, shell-command execution port, FLEXCUBE mutation port, or JIRA mutation capability.
- [X] T027 Implement the health endpoint and component status DTO in `backend/src/l1_support_bot/interface/api/routers/health.py` and `backend/src/l1_support_bot/interface/dto/health.py`.
- [X] T028 [P] Create the frontend application shell, route boundaries, shared API client, QueryClient provider, and error boundary in `frontend/src/app/App.tsx`, `frontend/src/app/router.tsx`, `frontend/src/app/providers.tsx`, `frontend/src/shared/api/client.ts`, and `frontend/src/shared/components/ErrorBoundary.tsx`.
- [X] T029 [P] Add frontend route and shell tests for `/chat`, `/config`, `/config/documents`, and `/config/ai` in `frontend/tests/components/app-routing.test.tsx`.
- [X] T030 Run the foundational gate: `uv run pytest backend/tests/unit backend/tests/api`, `uv run mypy backend/src/l1_support_bot --strict`, `uv run ruff check backend`, `uv run tach check`, and `npm test -- --run frontend` before starting story work.

**Checkpoint**: The domain/application boundaries, error model, configuration, logging, API
shell, frontend shell, and test harness are ready. No story can bypass this checkpoint.

---

## Phase 3: User Story 1 — Document Upload and Validation (Priority: P1) 🎯 MVP

**Plan mapping**: Plan Phase 1 — Document Registration and Storage.

**Goal**: A configuration user can upload a valid PDF, DOCX, or Markdown document and receive
an immediate queued response; invalid, oversized, duplicate, unreadable, or signature-mismatched
files are rejected safely.

**Independent test**: Upload one valid sample document and verify it is registered with a queued
status without waiting for ingestion. Exercise each invalid-file path and verify the knowledge
base is unchanged.

### Tests for User Story 1

- [X] T031 [P] [US1] Add upload validation unit tests for extension, MIME type, magic bytes, configured size limit, empty files, and malformed multipart input in `backend/tests/unit/application/ingestion/test_upload_validation.py`.
- [X] T032 [P] [US1] Add duplicate checksum and concurrent-upload repository tests in `backend/tests/unit/application/ingestion/test_duplicate_documents.py`.
- [X] T033 [P] [US1] Add local file-storage integration tests for safe filenames, path traversal attempts, atomic writes, checksum verification, cleanup, and deletion in `backend/tests/integration/file_storage/test_local_file_storage.py`.
- [X] T034 [P] [US1] Add API contract tests for upload, list, detail, and invalid-file responses in `backend/tests/api/test_documents.py` using `specs/002-flexcube-support-chatbot/contracts/api-contracts.md`.
- [X] T035 [P] [US1] Add frontend component tests for the upload form, supported-format validation, size error, duplicate error, and queued status in `frontend/tests/components/configuration/document-upload.test.tsx`.

### Implementation for User Story 1

- [X] T036 [P] [US1] Define the `Document` and initial `IngestionJob` persistence mappings in `backend/src/l1_support_bot/infrastructure/persistence/models/documents.py` and `backend/src/l1_support_bot/infrastructure/persistence/models/ingestion_jobs.py`.
- [X] T037 [P] [US1] Implement the filesystem `FileStoragePort` adapter with UUID-based names, path traversal protection, atomic writes, SHA-256 checksums, and cleanup in `backend/src/l1_support_bot/infrastructure/file_storage/local.py`.
- [X] T038 [P] [US1] Implement SQLAlchemy repository adapters for document registration and ingestion-job creation in `backend/src/l1_support_bot/infrastructure/persistence/sqlalchemy/document_repository.py` and `backend/src/l1_support_bot/infrastructure/persistence/sqlalchemy/ingestion_job_repository.py`.
- [X] T039 [US1] Create Alembic initial migration for `documents` and `ingestion_jobs` in `backend/alembic/versions/001_documents_and_jobs.py`, keeping the schema compatible with the selected relational persistence strategy.
- [X] T040 [US1] Implement file validation and upload orchestration in `backend/src/l1_support_bot/application/ingestion/upload_document.py`, including extension/signature checks, checksum duplicate detection, secure storage, registration, and job creation.
- [X] T041 [US1] Implement document list and detail use cases in `backend/src/l1_support_bot/application/ingestion/get_documents.py` and `backend/src/l1_support_bot/application/ingestion/get_document.py`.
- [X] T042 [US1] Implement document upload, list, and detail DTOs and routes in `backend/src/l1_support_bot/interface/dto/documents.py` and `backend/src/l1_support_bot/interface/api/routers/documents.py`; return `202 Accepted` for accepted uploads.
- [X] T043 [US1] Implement the initial document-management screens and API hooks in `frontend/src/features/configuration/pages/DocumentsPage.tsx`, `frontend/src/features/configuration/components/DocumentUpload.tsx`, `frontend/src/features/configuration/components/DocumentList.tsx`, and `frontend/src/features/configuration/api/documents.ts`.
- [X] T044 [US1] Add the first database-backed local development startup and migration instructions to `docs/development/local-setup.md`.
- [X] T045 [US1] Run the independent US1 validation using `backend/tests/unit/application/ingestion/`, `backend/tests/integration/file_storage/`, `backend/tests/api/test_documents.py`, and `frontend/tests/components/configuration/document-upload.test.tsx`.

**Checkpoint**: Valid files return `202` with `QUEUED`; unsupported, oversized, duplicate,
and signature-invalid files do not enter the registry; source files are safely stored.

---

## Phase 4: User Story 2 — Ingestion Progress and Failure Visibility (Priority: P1)

**Plan mapping**: Plan Phase 2 — Structured FLEXCUBE Ingestion.

**Goal**: Accepted documents progress through observable asynchronous states, including the
clarified `COMPLETED_WITH_WARNING` terminal state, and failures are visible without secrets or
stack traces.

**Independent test**: Upload a document, run the worker, poll the job endpoint, and verify
progress plus a terminal success, warning, or failure state.

### Tests for User Story 2

- [X] T046 [P] [US2] Add parser contract tests for PDF, DOCX, Markdown, page/heading preservation, table warnings, and unreadable files in `backend/tests/integration/parsing/test_parser_contract.py`.
- [X] T047 [P] [US2] Add FLEXCUBE metadata extraction unit tests for task codes, screen names, menu paths, prerequisites, modes, fields, procedures, error codes, JIRA IDs, and RCA references in `backend/tests/unit/infrastructure/parsing/test_flexcube_metadata.py`.
- [X] T048 [P] [US2] Add structure-aware chunking unit tests for section boundaries, table units, procedure grouping, overlap, maximum size, and source metadata in `backend/tests/unit/infrastructure/chunking/test_structure_aware_chunker.py`.
- [X] T049 [P] [US2] Add ingestion state-machine tests for valid transitions, invalid transitions, retry exhaustion, worker recovery, and `COMPLETED_WITH_WARNING` in `backend/tests/unit/application/ingestion/test_ingestion_state_machine.py`.
- [X] T050 [P] [US2] Add worker integration tests for queued-job claiming, duplicate-claim prevention, restart recovery, progress updates, and failure diagnostics in `backend/tests/integration/ingestion/test_worker.py`.
- [X] T051 [P] [US2] Add job-status API contract tests for active progress, failure detail sanitization, and completed-with-warning payloads in `backend/tests/api/test_ingestion.py`.
- [X] T052 [P] [US2] Add frontend status polling tests for active, failed, completed, and completed-with-warning states in `frontend/tests/components/configuration/document-status.test.tsx`.

### Implementation for User Story 2

- [X] T053 [P] [US2] Define parser-independent `ParsedDocument`, `DocumentElement`, `ParseWarning`, and FLEXCUBE metadata models in `backend/src/l1_support_bot/domain/models/parsed_document.py`.
- [X] T054 [P] [US2] Implement the Docling parser adapter in `backend/src/l1_support_bot/infrastructure/parsing/docling_parser.py`, preserving page, heading, list, table, note, warning, and procedure structure.
- [X] T055 [P] [US2] Implement PDF and DOCX fallback adapters in `backend/src/l1_support_bot/infrastructure/parsing/pymupdf_parser.py` and `backend/src/l1_support_bot/infrastructure/parsing/python_docx_parser.py`.
- [X] T056 [P] [US2] Implement parser-independent FLEXCUBE metadata extraction in `backend/src/l1_support_bot/infrastructure/parsing/flexcube_metadata_extractor.py`; preserve apparent source inconsistencies as diagnostics rather than correcting them.
- [X] T057 [P] [US2] Implement structure-aware chunking with configurable overlap and table/procedure handling in `backend/src/l1_support_bot/infrastructure/chunking/structure_aware_chunker.py`.
- [X] T058 [US2] Add `knowledge_chunks` and ingestion-diagnostics migration in `backend/alembic/versions/002_chunks_and_ingestion_diagnostics.py` and implement `ChunkRepository` in `backend/src/l1_support_bot/infrastructure/persistence/sqlalchemy/chunk_repository.py`.
- [X] T059 [US2] Implement atomic persistent job claiming, retry limits, restart recovery, and terminal-state handling in `backend/src/l1_support_bot/infrastructure/jobs/sqlalchemy_job_queue.py` and `backend/src/l1_support_bot/worker/runner.py`.
- [X] T060 [US2] Implement `ProcessDocument` orchestration through parsing, normalisation, metadata extraction, and chunking in `backend/src/l1_support_bot/application/ingestion/process_document.py`.
- [X] T061 [US2] Add job-status DTOs and `GET /api/v1/ingestion/jobs/{job_id}` route in `backend/src/l1_support_bot/interface/dto/ingestion.py` and `backend/src/l1_support_bot/interface/api/routers/ingestion.py`.
- [X] T062 [US2] Add warning and failure display behavior to `frontend/src/features/configuration/components/DocumentStatus.tsx`, `frontend/src/features/configuration/components/IngestionWarnings.tsx`, and `frontend/src/features/configuration/hooks/useIngestionStatus.ts`.
- [X] T063 [US2] Document parser and chunking evaluation cases and observed diagnostics in `docs/evaluation/phase2-ingestion-quality.md` without claiming unmeasured quality results.
- [X] T064 [US2] Run the independent US2 validation with the worker, sample documents, ingestion API tests in `backend/tests/api/test_ingestion.py`, parser tests in `backend/tests/integration/parsing/test_parser_contract.py`, chunker tests in `backend/tests/unit/infrastructure/chunking/test_structure_aware_chunker.py`, and frontend status tests in `frontend/tests/components/configuration/document-status.test.tsx`.

**Checkpoint**: Documents visibly progress asynchronously; parse failures are safe and
explainable; partial parse reaches `READY_FOR_INDEXING_WITH_WARNING`, remains non-queryable,
and identifies missing content; only successful embedding and vector indexing can produce
`COMPLETED` or `COMPLETED_WITH_WARNING`; full failure reaches `FAILED`.

---

## Phase 5: User Story 3 — Grounded FLEXCUBE Question Answering (Priority: P1)

**Plan mapping**: Plan Phases 3–5 — Embeddings, Vector Index, Hybrid Retrieval foundation,
and Grounded Chatbot foundation.

**Goal**: A branch user can ask a direct FLEXCUBE task-code, screen, menu-path, prerequisite,
mode, field, procedure, or error-code question and receive an evidence-grounded answer.

**Independent test**: Index a sample document containing BA435, ask "What is task code BA435?",
and verify the answer is generated only from retrieved knowledge.

### Tests for User Story 3

- [X] T065 [P] [US3] Add embedding-port contract tests for batch generation, query generation, dimensions, timeout, and provider failure in `backend/tests/unit/domain/ports/test_embedding_port.py`.
- [X] T066 [P] [US3] Add Qdrant vector-store adapter integration tests for collection creation, upsert, payload metadata, dense search, and model compatibility in `backend/tests/integration/vector_store/test_qdrant_adapter.py`.
- [X] T067 [P] [US3] Add end-to-end ingestion-to-vector tests using a deterministic embedding fake in `backend/tests/integration/ingestion/test_indexing_pipeline.py`.
- [X] T068 [P] [US3] Add direct FLEXCUBE question tests for task code, screen, menu path, prerequisites, modes, fields, procedures, and error codes in `backend/tests/unit/application/retrieval/test_direct_flexcube_questions.py`.
- [X] T069 [P] [US3] Add chat API contract tests for supported grounded-answer responses in `backend/tests/api/test_chat_grounded.py`.
- [X] T070 [P] [US3] Add ChatPage and message rendering tests in `frontend/tests/components/chatbot/chat-page.test.tsx`.

### Implementation for User Story 3

- [X] T071 [P] [US3] Define embedding configuration and vector payload models in `backend/src/l1_support_bot/domain/models/embedding.py` and `backend/src/l1_support_bot/domain/models/vector_index.py`.
- [X] T072 [P] [US3] Implement the configurable HTTP embedding adapter in `backend/src/l1_support_bot/infrastructure/embedding/http_embedding.py`; keep provider SDK/protocol details inside the adapter.
- [X] T073 [P] [US3] Implement the vector-store port adapter for Qdrant in `backend/src/l1_support_bot/infrastructure/vector_store/qdrant_store.py`, including payload filters and index compatibility checks.
- [X] T074 [US3] Add embedding configuration and chunk-index migrations in `backend/alembic/versions/003_embedding_configuration.py` and `backend/src/l1_support_bot/infrastructure/persistence/sqlalchemy/configuration_repository.py`.
- [ ] T209 [US3] Evaluate Qwen3-Embedding, BGE-M3, and nomic-embed-text using representative FLEXCUBE retrieval fixtures. Measure Recall@5, Recall@10, MRR, exact-identifier hit rate, latency, vector dimensionality, storage impact, licensing, and local/external deployment feasibility. Record results and the provisional selection without fabricating results in `docs/evaluation/embedding-model-evaluation.md` and the relevant embedding-model ADR at `docs/adr/ADR-005-embedding-model.md`.
- [X] T075 [US3] Extend `ProcessDocument` in `backend/src/l1_support_bot/application/ingestion/process_document.py` through batching, embedding, index validation, `COMPLETED`, and `COMPLETED_WITH_WARNING` outcomes.
- [X] T076 [US3] Implement embedding-model compatibility checks and explicit re-index requirement in `backend/src/l1_support_bot/application/configuration/validate_embedding_compatibility.py`.
- [X] T077 [US3] Define retrieval result, context chunk, answer type, and grounded answer domain models in `backend/src/l1_support_bot/domain/models/answer.py` and `backend/src/l1_support_bot/domain/models/retrieval.py`.
- [X] T078 [US3] Implement the initial dense retrieval orchestration in `backend/src/l1_support_bot/application/retrieval/dense_retrieval.py` using `RetrieverPort` and `VectorStore` only.
- [X] T122 [P] [US3] Add hybrid retrieval fusion tests for dense, lexical, exact-identifier, metadata filters, and RRF/weighted fusion in `backend/tests/unit/infrastructure/retrieval/test_hybrid_retriever.py`.
- [X] T125 [P] [US3] Implement exact identifier extraction and normalization in `backend/src/l1_support_bot/infrastructure/retrieval/identifier_extractor.py`.
- [X] T126 [P] [US3] Implement lexical retrieval and sparse candidate generation in `backend/src/l1_support_bot/infrastructure/retrieval/lexical_retriever.py`.
- [X] T127 [US3] Implement dense-plus-lexical-plus-exact hybrid fusion, deduplication, metadata filtering, and configurable weighting in `backend/src/l1_support_bot/infrastructure/retrieval/hybrid_retriever.py`.
- [X] T130 [US3] Add retrieval configuration model, repository, migration, DTOs, and routes in `backend/src/l1_support_bot/domain/models/retrieval_config.py`, `backend/src/l1_support_bot/infrastructure/persistence/sqlalchemy/retrieval_config_repository.py`, `backend/alembic/versions/004_retrieval_configuration.py`, and `backend/src/l1_support_bot/interface/api/routers/retrieval_config.py`.
- [X] T132 [US3] Run the 50-question dense-only versus hybrid retrieval evaluation and record Recall@5, Recall@10, MRR, exact-identifier hit rate, and latency in `docs/evaluation/phase4-retrieval-baseline.md`.
- [X] T079 [US3] Implement the LLM port and Ollama HTTP adapter in `backend/src/l1_support_bot/domain/ports/llm.py` and `backend/src/l1_support_bot/infrastructure/llm/ollama_client.py` with timeout, retry, health-check, and controlled failure mapping.
- [X] T080 [US3] Implement context assembly and grounded prompt construction in `backend/src/l1_support_bot/application/retrieval/context_assembler.py`, `backend/src/l1_support_bot/application/retrieval/prompt_builder.py`, and `backend/src/l1_support_bot/infrastructure/prompts/system_prompt_v1.txt`.
- [X] T081 [US3] Implement the `AskQuestion` use case in `backend/src/l1_support_bot/application/retrieval/ask_question.py`, ensuring the LLM never directly queries the vector store and receives only framed retrieved context.
- [X] T082 [US3] Implement chat session creation and the initial chat endpoint in `backend/src/l1_support_bot/application/session/start_chat_session.py`, `backend/src/l1_support_bot/interface/api/routers/sessions.py`, and `backend/src/l1_support_bot/interface/api/routers/chat.py`.
- [X] T083 [US3] Implement the Branch User Chatbot route and core components in `frontend/src/features/chatbot/pages/ChatPage.tsx`, `frontend/src/features/chatbot/components/ChatInput.tsx`, `frontend/src/features/chatbot/components/MessageList.tsx`, and `frontend/src/features/chatbot/api/chat.ts`.
- [X] T084 [US3] Add the provisional Ollama development setup and model replacement guidance to `docs/development/local-setup.md` and `docs/architecture/llm.md`.
- [ ] T085 [US3] Run the independent US3 validation on an indexed FLEXCUBE fixture using `backend/tests/integration/ingestion/test_indexing_pipeline.py`, `backend/tests/integration/vector_store/test_qdrant_adapter.py`, and `backend/tests/api/test_chat_grounded.py` with a configured Ollama-compatible model.

**Checkpoint**: A supported direct question returns a grounded answer candidate; no LLM,
provider SDK, or vector-store implementation leaks into the domain/application core.

---

## Phase 6: User Story 4 — Mandatory Source Citations (Priority: P1)

**Plan mapping**: Plan Phase 5 — Grounded Chatbot response validation and citation handling.

**Goal**: Every supported answer visibly cites only the source chunks that materially support
its claims, with document and available source-location metadata.

**Independent test**: Ask a supported question and verify a source citation; ask an unsupported
question and verify no citation; inspect the cited chunk ID against retrieved results.

- [X] T086 [P] [US4] Add citation construction and validation unit tests for document name, page, section, task code, screen name, chunk identity, deleted documents, and incomplete metadata in `backend/tests/unit/application/retrieval/test_citation_validation.py`.
- [X] T087 [P] [US4] Add response-schema tests for grounded answers, citation absence on insufficient responses, and rejection of fabricated citation IDs in `backend/tests/unit/application/retrieval/test_response_validator.py`.
- [X] T088 [P] [US4] Add API contract tests for citation fields and source-location omission behavior in `backend/tests/api/test_citation_contract.py`.
- [X] T089 [P] [US4] Add frontend citation rendering tests for document name, page, section, task code, missing page, and multiple citations in `frontend/tests/components/chatbot/citation-list.test.tsx`.
- [X] T090 [P] [US4] Define the citation domain model and citation response DTO in `backend/src/l1_support_bot/domain/models/citation.py` and `backend/src/l1_support_bot/interface/dto/citations.py`.
- [X] T091 [US4] Implement citation construction from retrieved chunks and answer references in `backend/src/l1_support_bot/application/retrieval/citation_builder.py`.
- [X] T092 [US4] Implement response validation for citation presence, citation-to-retrieval membership, source existence, and citation coverage in `backend/src/l1_support_bot/application/retrieval/response_validator.py`.
- [X] T093 [US4] Extend the answer DTO and chat route in `backend/src/l1_support_bot/interface/dto/chat.py` and `backend/src/l1_support_bot/interface/api/routers/chat.py` to return validated citations only.
- [X] T094 [US4] Implement citation rendering and accessible source labels in `frontend/src/features/chatbot/components/CitationList.tsx` and `frontend/src/features/chatbot/components/CitationItem.tsx`.
- [X] T095 [US4] Document citation traceability from source document to parsed element, chunk, retrieval result, context, answer, and UI in `docs/architecture/citations.md`.
- [X] T096 [US4] Run the independent US4 validation with citation fixtures in `backend/tests/unit/application/retrieval/test_citation_validation.py`, `backend/tests/unit/application/retrieval/test_response_validator.py`, and `frontend/tests/components/chatbot/citation-list.test.tsx`, verifying SC-001, SC-006, and SC-007 behavior.

**Checkpoint**: Supported answers contain validated citations; unsupported responses do not
invent or attach citations; absent page numbers are omitted rather than fabricated.

---

## Phase 7: User Story 5 — Insufficient Information Response (Priority: P1)

**Plan mapping**: Plan Phase 4–5 — Evidence sufficiency, response validation, and safe fallback.

**Goal**: The chatbot refuses to answer from general model knowledge when evidence is absent
or below configured confidence and clearly distinguishes insufficient evidence from service failure.

**Independent test**: Ask an out-of-knowledge-base question with an available LLM and verify an
explicit insufficient-information response with no domain claims or citations.

- [X] T097 [P] [US5] Add evidence-sufficiency tests for no results, low score, low token evidence, exact-identifier exceptions, and partially available evidence in `backend/tests/unit/application/retrieval/test_evidence_sufficiency.py`.
- [X] T098 [P] [US5] Add unsupported and incorrect-premise chat tests in `backend/tests/unit/application/retrieval/test_insufficient_information.py`.
- [X] T099 [P] [US5] Add API tests distinguishing `INSUFFICIENT` from `LLM_UNAVAILABLE` and `VECTOR_STORE_UNAVAILABLE` in `backend/tests/api/test_chat_failure_and_insufficient.py`.
- [X] T100 [P] [US5] Add frontend tests for insufficient, partial, and service-failure response states in `frontend/tests/components/chatbot/response-states.test.tsx`.
- [X] T101 [P] [US5] Implement evidence-sufficiency policy and threshold validation in `backend/src/l1_support_bot/application/retrieval/evidence_sufficiency.py`.
- [X] T102 [US5] Implement the `InsufficientInfoResponse`, partial-answer, ambiguous-answer, and incorrect-premise result paths in `backend/src/l1_support_bot/application/retrieval/answer_outcomes.py`.
- [X] T103 [US5] Update `AskQuestion` in `backend/src/l1_support_bot/application/retrieval/ask_question.py` to return insufficient information before LLM generation when evidence is inadequate.
- [X] T104 [US5] Add user-safe response-state DTOs and error mapping in `backend/src/l1_support_bot/interface/dto/chat.py` and `backend/src/l1_support_bot/interface/api/middleware/errors.py`.
- [X] T105 [US5] Implement explicit insufficient-information and partial-answer UI states in `frontend/src/features/chatbot/components/ResponseState.tsx` and `frontend/src/features/chatbot/components/MessageBubble.tsx`.
- [X] T106 [US5] Add an evaluation fixture for known-answer and unanswerable FLEXCUBE questions in `backend/tests/eval/insufficient_information_cases.json`.
- [X] T107 [US5] Run the independent US5 validation with `backend/tests/unit/application/retrieval/test_insufficient_information.py`, `backend/tests/unit/application/retrieval/test_evidence_sufficiency.py`, and `backend/tests/api/test_chat_failure_and_insufficient.py`, verifying no unsupported domain claim is produced.

**Checkpoint**: Evidence gaps yield an honest response; an unavailable dependency yields a
service error; neither path falls back to ungrounded generation.

---

## Phase 8: User Story 6 — Session-Level Follow-Up Questions (Priority: P2)

**Plan mapping**: Plan Phase 6 — Conversation and Feedback, session portion.

**Goal**: A branch user can ask follow-up questions in a bounded, expiring session while
conversation history remains context only, never factual evidence.

**Independent test**: Ask about BA435, ask "What are its prerequisites?", then clear the session
and verify the same pronoun-dependent question is treated as a fresh query.

- [X] T108 [P] [US6] Add session lifecycle, expiry, clear, history-window, and token-budget tests in `backend/tests/unit/application/session/test_session_manager.py`.
- [X] T109 [P] [US6] Add follow-up query-resolution tests for pronouns, topic references, ambiguous history, cleared history, and expired sessions in `backend/tests/unit/application/session/test_query_resolution.py`.
- [X] T110 [P] [US6] Add session API tests for create, clear, expired session, and bounded history behavior in `backend/tests/api/test_sessions.py`.
- [X] T111 [P] [US6] Add frontend tests for chat history, clear-session, expired-session, and follow-up state in `frontend/tests/components/chatbot/session.test.tsx`.
- [X] T112 [P] [US6] Implement the session-store port and bounded in-memory session manager in `backend/src/l1_support_bot/domain/ports/session_store.py` and `backend/src/l1_support_bot/infrastructure/session/in_memory_session_store.py`.
- [X] T113 [US6] Implement session lifecycle use cases and expiry enforcement in `backend/src/l1_support_bot/application/session/session_manager.py`.
- [X] T114 [US6] Implement bounded history selection, token-budget accounting, and follow-up query resolution in `backend/src/l1_support_bot/application/session/query_resolution.py`.
- [X] T115 [US6] Update `AskQuestion` in `backend/src/l1_support_bot/application/retrieval/ask_question.py` to separate conversational context from retrieved evidence and to retrieve fresh evidence for every domain answer.
- [X] T116 [US6] Add clear-session route and session-expiry error contract in `backend/src/l1_support_bot/interface/api/routers/sessions.py` and `backend/src/l1_support_bot/interface/dto/sessions.py`.
- [X] T117 [US6] Add session context provider, clear action, expiry recovery, and bounded message history to `frontend/src/features/chatbot/hooks/useChatSession.ts`, `frontend/src/features/chatbot/components/ChatSessionControls.tsx`, and `frontend/src/features/chatbot/pages/ChatPage.tsx`.
- [X] T118 [US6] Document session privacy, retention, expiry, and evidence separation in `docs/architecture/sessions.md`.
- [X] T119 [US6] Run the independent US6 validation with `backend/tests/unit/application/session/test_query_resolution.py`, `backend/tests/unit/application/session/test_session_manager.py`, `backend/tests/api/test_sessions.py`, and `frontend/tests/components/chatbot/session.test.tsx` for follow-up, clear, expiry, and evidence-grounding scenarios.

**Checkpoint**: Follow-ups are convenient but bounded; clearing or expiry removes context;
history never substitutes for knowledge-base retrieval.

---

## Phase 9: User Story 7 — Multi-Source and Partially Supported Answers (Priority: P2)

**Plan mapping**: Plan Phases 4, 5, and 7 — Hybrid retrieval, response outcomes, and optional
reranking experiment.

**Goal**: The chatbot combines multiple relevant sources, labels partial coverage, and
surfaces ambiguity without silently choosing unsupported interpretations.

**Independent test**: Index two related documents, ask a cross-source question, and verify
both supporting citations; ask an ambiguous question and verify ambiguity is communicated.

- [X] T120 [P] [US7] Add multi-source retrieval and candidate-deduplication tests in `backend/tests/unit/application/retrieval/test_multi_source_context.py`.
- [X] T121 [P] [US7] Add partial-coverage and ambiguous-question outcome tests in `backend/tests/unit/application/retrieval/test_partial_and_ambiguous_answers.py`.
- [X] T123 [P] [US7] Add multi-document chat API contract tests in `backend/tests/api/test_multi_source_chat.py`.
- [X] T124 [P] [US7] Add frontend tests for multiple citations, partial-answer labels, ambiguity prompts, and unsupported premise messaging in `frontend/tests/components/chatbot/multi-source-and-ambiguity.test.tsx`.
- [X] T128 [US7] Update `ContextAssembler` in `backend/src/l1_support_bot/application/retrieval/context_assembler.py` to retain multiple document sources while respecting evidence and context-size limits.
- [X] T129 [US7] Implement partial-answer and ambiguity classification in `backend/src/l1_support_bot/application/retrieval/answer_outcomes.py` without adding undocumented FLEXCUBE claims.
- [X] T131 [US7] Implement the replaceable reranker port and provisional FlashRank adapter in `backend/src/l1_support_bot/domain/ports/reranker.py` and `backend/src/l1_support_bot/infrastructure/reranking/flashrank_reranker.py`.
- [ ] T133 [US7] Run the 100-question no-rerank versus rerank experiment and record quality, latency, resource, licensing, and operational findings in `docs/evaluation/phase7-reranking.md`.
- [ ] T134 [US7] Record the evidence-based hybrid retrieval and reranking decisions in `docs/adr/ADR-010-hybrid-retrieval.md` and `docs/adr/ADR-017-reranking.md`.
- [X] T135 [US7] Update the frontend to display multi-source citations, partial coverage, and ambiguity outcomes in `frontend/src/features/chatbot/components/CitationList.tsx`, `frontend/src/features/chatbot/components/ResponseState.tsx`, and `frontend/src/features/chatbot/components/ClarificationPrompt.tsx`.
- [X] T136 [US7] Run the independent US7 validation with `backend/tests/unit/application/retrieval/test_multi_source_context.py`, `backend/tests/unit/application/retrieval/test_partial_and_ambiguous_answers.py`, `backend/tests/api/test_multi_source_chat.py`, and `frontend/tests/components/chatbot/multi-source-and-ambiguity.test.tsx`.

**Checkpoint**: Hybrid retrieval is measurable and configurable; multi-source answers cite
supporting documents; ambiguity and partial coverage are explicit.

---

## Phase 10: User Story 8 — Document Deletion and Re-indexing (Priority: P2)

**Plan mapping**: Plan Phases 1, 3, and 9 — lifecycle operations, vector index replacement,
and hardening. Deletion policy follows the resolved T013 decision.

**Goal**: Deletion removes all retrievable content, while re-indexing builds and validates a
replacement before cutover and preserves the prior usable index on failure.

**Independent test**: Index a document, delete it, verify it cannot be retrieved; then re-index
a document with a forced failure and verify the prior index remains usable.

- [X] T137 [P] [US8] Add deletion tests for completed, completed-with-warning, failed, and active-ingestion states using the confirmed Q2 policy in `backend/tests/unit/application/ingestion/test_delete_document.py`.
- [X] T138 [P] [US8] Add vector cleanup and orphan-prevention integration tests in `backend/tests/integration/vector_store/test_document_cleanup.py`.
- [X] T139 [P] [US8] Add re-index atomic cutover, failure rollback, concurrent-query, and stale-index tests in `backend/tests/integration/ingestion/test_reindex_atomicity.py`.
- [X] T140 [P] [US8] Add API contract tests for delete, re-index, active-ingestion conflict, and cleanup failure in `backend/tests/api/test_document_lifecycle.py`.
- [X] T141 [P] [US8] Add frontend tests for delete confirmation, in-progress conflict, re-index progress, and failure recovery in `frontend/tests/components/configuration/document-lifecycle.test.tsx`.
- [X] T142 [US8] Implement deletion use case and confirmed active-ingestion conflict behavior in `backend/src/l1_support_bot/application/ingestion/delete_document.py`.
- [X] T143 [US8] Implement vector deletion, relational chunk cleanup, safe source-file deletion, and failure recovery in `backend/src/l1_support_bot/application/ingestion/cleanup_document.py`.
- [X] T144 [US8] Implement deterministic re-index staging, validation, atomic collection/namespace cutover, and old-index cleanup in `backend/src/l1_support_bot/application/ingestion/reindex_document.py` and `backend/src/l1_support_bot/infrastructure/vector_store/qdrant_index_manager.py`.
- [X] T145 [US8] Add delete and re-index routes, DTOs, status responses, and conflict errors in `backend/src/l1_support_bot/interface/api/routers/documents.py`, `backend/src/l1_support_bot/interface/api/routers/ingestion.py`, and `backend/src/l1_support_bot/interface/dto/document_lifecycle.py`.
- [X] T146 [US8] Add delete confirmation, re-index action, and lifecycle status UI in `frontend/src/features/configuration/components/DeleteDocumentDialog.tsx`, `frontend/src/features/configuration/components/ReindexDocumentButton.tsx`, and `frontend/src/features/configuration/pages/DocumentsPage.tsx`.
- [X] T147 [US8] Document index consistency, staging, cutover, rollback, and orphan cleanup in `docs/architecture/index-consistency.md`.
- [X] T148 [US8] Run the independent US8 validation with `backend/tests/unit/application/ingestion/test_delete_document.py`, `backend/tests/integration/ingestion/test_reindex_atomicity.py`, `backend/tests/integration/vector_store/test_document_cleanup.py`, and `backend/tests/api/test_document_lifecycle.py` for delete-after-index, the T013 deletion policy, rollback, cutover, and concurrent chat queries.

**Checkpoint**: Deleted documents are not retrievable; re-indexing never exposes a partial
or mixed index; failed re-indexing preserves the previous usable index.

---

## Phase 11: User Story 9 — Feedback Submission (Priority: P2)

**Plan mapping**: Plan Phase 6 — Conversation and Feedback, feedback portion.

**Goal**: Branch users can submit helpful/not-helpful feedback with an optional comment,
and feedback is stored for review without changing system behavior automatically.

**Independent test**: Submit feedback for an answer, verify the response, persisted context,
and unchanged subsequent behavior.

- [X] T149 [P] [US9] Add feedback domain validation tests for rating, comment length, required answer linkage, and no-auto-update invariant in `backend/tests/unit/application/feedback/test_feedback_validation.py`.
- [X] T150 [P] [US9] Add feedback persistence integration tests for question, answer, session, citations, configuration snapshot, and timestamp in `backend/tests/integration/persistence/test_feedback_repository.py`.
- [X] T151 [P] [US9] Add feedback API contract tests in `backend/tests/api/test_feedback.py`.
- [X] T152 [P] [US9] Add frontend feedback control, optional comment, disabled-submit, and confirmation tests in `frontend/tests/components/chatbot/feedback.test.tsx`.
- [X] T153 [P] [US9] Define the Feedback domain model and repository port in `backend/src/l1_support_bot/domain/models/feedback.py` and `backend/src/l1_support_bot/domain/ports/feedback_repository.py`.
- [X] T154 [US9] Add the feedback persistence migration and repository implementation in `backend/alembic/versions/005_feedback.py` and `backend/src/l1_support_bot/infrastructure/persistence/sqlalchemy/feedback_repository.py`.
- [X] T155 [US9] Implement `SubmitFeedback` enrichment and persistence in `backend/src/l1_support_bot/application/feedback/submit_feedback.py`, including retrieved chunk IDs and configuration identifiers where available.
- [X] T156 [US9] Implement the feedback request/response DTO and route in `backend/src/l1_support_bot/interface/dto/feedback.py` and `backend/src/l1_support_bot/interface/api/routers/feedback.py`.
- [X] T157 [US9] Implement feedback controls and confirmation state in `frontend/src/features/chatbot/components/FeedbackForm.tsx` and `frontend/src/features/chatbot/components/MessageBubble.tsx`.
- [X] T158 [US9] Document supervised feedback use and the prohibition on automatic prompt, model, retrieval, or knowledge-base changes in `docs/architecture/feedback.md`.
- [X] T159 [US9] Run the independent US9 validation with `backend/tests/integration/persistence/test_feedback_repository.py`, `backend/tests/api/test_feedback.py`, and `frontend/tests/components/chatbot/feedback.test.tsx`, verifying feedback persistence plus unchanged chatbot configuration and answer behavior.

**Checkpoint**: Feedback is captured reliably, linked to the answer context, and has no
automatic effect on system behavior.

---

## Phase 12: User Story 10 — Safe Failure Handling (Priority: P2)

**Plan mapping**: Plan Phase 9 — Hardening and Readiness Assessment, plus cross-cutting errors.

**Goal**: Service failures yield safe, sanitized responses; where feasible, indexed answering
continues in explicit read-only degraded mode when optional metadata persistence is unavailable.

**Independent test**: Simulate LLM, vector store, and metadata persistence failures separately;
verify safe error or degraded response for each.

- [X] T160 [P] [US10] Add application tests for LLM unavailable, embedding unavailable, vector store unavailable, database unavailable, timeout, retry exhaustion, and no-fabrication fallback in `backend/tests/unit/application/test_failure_boundaries.py`.
- [X] T161 [P] [US10] Add API tests for sanitized error schemas, status codes, request IDs, and degraded health payloads in `backend/tests/api/test_error_handling.py`.
- [X] T162 [P] [US10] Add degraded-mode integration tests for cached runtime configuration, indexed answering, read-only restrictions, and recovery in `backend/tests/integration/degraded_mode/test_oracle_unavailable.py`.
- [X] T163 [P] [US10] Add frontend tests for service-unavailable, limited-mode banner, retry, and disabled configuration operations in `frontend/tests/components/shared/failure-states.test.tsx`.
- [X] T164 [P] [US10] Implement safe infrastructure error mapping and retry boundary utilities in `backend/src/l1_support_bot/application/shared/retry_policy.py` and `backend/src/l1_support_bot/application/shared/failure_mapping.py`.
- [X] T165 [US10] Implement runtime configuration cache loading, health state, and explicit degraded-mode capability checks in `backend/src/l1_support_bot/infrastructure/configuration/runtime_config_cache.py` and `backend/src/l1_support_bot/application/configuration/runtime_health.py`.
- [X] T166 [US10] Update the chat use case and API dependencies to answer from cached configuration only when retrieval and LLM are available, while rejecting persistence-dependent mutations in `backend/src/l1_support_bot/application/retrieval/ask_question.py` and `backend/src/l1_support_bot/interface/dependencies.py`.
- [X] T167 [US10] Add degraded capability status to health and API responses in `backend/src/l1_support_bot/interface/api/routers/health.py` and `backend/src/l1_support_bot/interface/dto/health.py`.
- [X] T168 [US10] Add safe failure logging with error categories, durations, and no sensitive content in `backend/src/l1_support_bot/interface/logging.py` and affected application modules.
- [X] T169 [US10] Implement user-facing failure, retry, and limited-mode presentation in `frontend/src/shared/api/error-handler.ts`, `frontend/src/shared/components/DegradedModeBanner.tsx`, and `frontend/src/features/chatbot/components/ResponseState.tsx`.
- [X] T170 [US10] Run the independent US10 validation matrix with `backend/tests/unit/application/test_failure_boundaries.py`, `backend/tests/api/test_error_handling.py`, `backend/tests/integration/degraded_mode/test_oracle_unavailable.py`, and `frontend/tests/components/shared/failure-states.test.tsx`.

**Checkpoint**: No infrastructure failure produces a fabricated answer; degraded mode is
explicit, read-only for mutations, and communicated without internal details.

---

## Phase 13: User Story 11 — Prompt Injection Resistance (Priority: P1)

**Plan mapping**: Plan Phase 5 and Phase 9 — grounded prompt controls, security review, and
adversarial evaluation.

**Goal**: User and document instructions are treated as untrusted content; prompts, secrets,
configuration, and autonomous actions are not exposed or executed.

**Independent test**: Submit user and document injection fixtures and verify grounding,
non-disclosure, and no command execution behavior.

- [X] T171 [P] [US11] Add user-query injection tests for instruction override, system-prompt disclosure, general-knowledge requests, command requests, and configuration disclosure in `backend/tests/unit/application/security/test_query_prompt_injection.py`.
- [X] T172 [P] [US11] Add document-content injection tests for embedded instructions, malicious markup, executable-looking content, and passive-reference framing in `backend/tests/integration/security/test_document_prompt_injection.py`.
- [X] T173 [P] [US11] Add API tests verifying secrets, prompts, internal metadata, and stack traces never appear in responses in `backend/tests/api/test_security_disclosure.py`.
- [X] T174 [P] [US11] Add frontend tests ensuring system prompt, secrets, infrastructure configuration, and internal errors are not rendered in `frontend/tests/components/security/non-disclosure.test.tsx`.
- [X] T175 [P] [US11] Implement bounded query normalization and injection-pattern categorization in `backend/src/l1_support_bot/application/security/query_sanitizer.py`; preserve the original user intent without logging raw query content.
- [X] T176 [US11] Harden context framing and versioned system prompt instructions in `backend/src/l1_support_bot/infrastructure/prompts/system_prompt_v1.txt` and `backend/src/l1_support_bot/application/retrieval/prompt_builder.py`.
- [X] T177 [US11] Add response disclosure checks and safe rejection behavior in `backend/src/l1_support_bot/application/security/response_disclosure_validator.py`.
- [X] T178 [US11] Verify all document parsers and storage paths do not execute embedded files, macros, links, or document instructions in `backend/src/l1_support_bot/infrastructure/parsing/` and `backend/src/l1_support_bot/infrastructure/file_storage/`.
- [X] T179 [US11] Add adversarial prompt-injection cases to `backend/tests/eval/security_cases.json` and record deterministic and human-reviewed results in `docs/evaluation/security-injection-results.md`.
- [X] T180 [US11] Run the independent US11 security validation with `backend/tests/unit/application/security/test_query_prompt_injection.py`, `backend/tests/integration/security/test_document_prompt_injection.py`, `backend/tests/api/test_security_disclosure.py`, and `frontend/tests/components/security/non-disclosure.test.tsx`, confirming SC-021.

**Checkpoint**: Documents remain passive reference material; user instructions cannot change
system behavior; no unauthorized execution capability exists.

---

## Phase 14: User Story 12 — AI and RAG Configuration Management (Priority: P2)

**Plan mapping**: Plan Phase 8 — Configuration Capabilities.

**Goal**: Configuration users can safely view and change approved AI/RAG settings without
exposing secrets; incompatible embedding changes require explicit re-index handling.

**Independent test**: View masked settings, save a valid retrieval change, reject an unreachable
LLM endpoint, and require re-index confirmation for an embedding model change.

- [X] T181 [P] [US12] Add configuration validation unit tests for LLM, embedding, retrieval, chunking, timeout, retry, threshold, weight, and compatibility rules in `backend/tests/unit/application/configuration/test_configuration_validation.py`.
- [X] T182 [P] [US12] Add configuration API contract tests for masked secrets, connectivity validation, invalid values, rollback-on-failure, and re-index warnings in `backend/tests/api/test_configuration.py`.
- [X] T183 [P] [US12] Add frontend configuration-form tests for validation, masked credentials, connectivity errors, compatibility warnings, and save confirmation in `frontend/tests/components/configuration/ai-configuration.test.tsx`.
- [X] T184 [P] [US12] Define LLM, embedding, retrieval, and chunking configuration domain models in `backend/src/l1_support_bot/domain/models/configuration.py`.
- [X] T185 [US12] Implement configuration repositories and migrations for LLM, embedding, retrieval, and chunking settings in `backend/src/l1_support_bot/infrastructure/persistence/sqlalchemy/configuration_repository.py` and `backend/alembic/versions/006_ai_rag_configuration.py`.
- [X] T186 [US12] Implement LLM and embedding connectivity validation use cases in `backend/src/l1_support_bot/application/configuration/validate_llm.py` and `backend/src/l1_support_bot/application/configuration/validate_embedding.py`.
- [X] T187 [US12] Implement transactional configuration activation with rollback on validation failure in `backend/src/l1_support_bot/application/configuration/update_configuration.py`.
- [X] T188 [US12] Implement explicit embedding and chunking re-index requirement checks in `backend/src/l1_support_bot/application/configuration/validate_index_compatibility.py`.
- [X] T189 [US12] Implement configuration DTOs and GET/PUT/validate routes in `backend/src/l1_support_bot/interface/dto/configuration.py` and `backend/src/l1_support_bot/interface/api/routers/configuration.py`.
- [X] T190 [US12] Implement the Configuration AI settings pages and forms in `frontend/src/features/configuration/pages/AIConfigPage.tsx`, `frontend/src/features/configuration/components/LLMConfigForm.tsx`, `frontend/src/features/configuration/components/EmbeddingConfigForm.tsx`, `frontend/src/features/configuration/components/RetrievalConfigForm.tsx`, and `frontend/src/features/configuration/components/ChunkingConfigForm.tsx`.
- [X] T191 [US12] Add safe masked-secret display and re-index warning UI in `frontend/src/features/configuration/components/MaskedSecretField.tsx` and `frontend/src/features/configuration/components/ReindexWarning.tsx`.
- [X] T192 [US12] Document configuration precedence, runtime/restart behavior, compatibility, rollback, and secret handling in `docs/architecture/configuration.md`.
- [X] T193 [US12] Run the independent US12 validation with `backend/tests/unit/application/configuration/test_configuration_validation.py`, `backend/tests/api/test_configuration.py`, and `frontend/tests/components/configuration/ai-configuration.test.tsx` for valid changes, rejected changes, endpoint failures, masked values, and embedding compatibility warnings.

**Checkpoint**: Configuration changes are validated before activation; failed changes do not
replace active configuration; secrets are never returned or displayed.

---

## Phase 15: Polish and Cross-Cutting Readiness (Plan Phase 9)

**Purpose**: Complete cross-cutting quality gates, documentation, RAG evaluation, security
review, and local quickstart validation. These tasks do not add new user-story scope.

- [x] T194 [P] Add backend dependency, license, and vulnerability review notes to `docs/security/dependency-review.md` without introducing CI/CD.
- [x] T195 [P] Add the OWASP-oriented application security review checklist to `docs/security/application-security-review.md`, covering uploads, path traversal, CORS, input/output handling, secrets, prompt injection, and error disclosure.
- [x] T196 [P] Add large-document and memory-behavior test fixtures and execution notes to `backend/tests/integration/parsing/test_large_documents.py` and `docs/evaluation/large-document-characterization.md` without inventing performance targets.
- [x] T197 [P] Create the initial 100-case RAG evaluation dataset and groundedness review rubric in `backend/tests/eval/rag_cases.json`, covering task codes, screens, procedures, errors, JIRA, RCA, multi-source, ambiguity, unsupported, and injection cases. Define the evaluation sample as 100 cases with an explicit answerability label; use two independent reviewers with FLEXCUBE L1 support or domain expertise; count a claim as evidence-supported only when the indexed source entails it; require partially supported answers to label unsupported portions explicitly; require every displayed citation to be locatable and materially support its claim; resolve reviewer disagreements by adjudication; and calculate SC-003 as passed answerable cases divided by all answerable cases, passing only when the rate is at least 90%. Record no results until the evaluation is run.
- [x] T198 [P] Implement deterministic retrieval metric calculation in `backend/src/l1_support_bot/evaluation/retrieval_metrics.py` and generation/citation result recording in `backend/src/l1_support_bot/evaluation/generation_metrics.py`.
- [x] T199 [P] Add RAG evaluation run orchestration and configuration snapshot persistence in `backend/src/l1_support_bot/application/evaluation/run_rag_evaluation.py` and `backend/src/l1_support_bot/infrastructure/persistence/sqlalchemy/evaluation_repository.py`.
- [x] T200 [P] Add frontend accessibility checks for ChatPage, DocumentsPage, configuration forms, loading states, errors, and citations in `frontend/tests/e2e/accessibility.spec.ts`.
- [x] T201 Add end-to-end Playwright coverage for upload → ingest → chat → citation → feedback → delete in `frontend/tests/e2e/l1-support-bot.spec.ts`.
- [x] T202 Add failure-path end-to-end coverage for invalid document, parser failure, embedding failure, vector-store failure, LLM failure, Oracle degraded mode, and prompt injection in `frontend/tests/e2e/failure-and-security.spec.ts`.
- [x] T203 Add backend and frontend startup instructions, optional Oracle configuration, Qdrant standalone setup, Ollama setup, embedding setup, and degraded-mode limitations to `docs/development/local-setup.md`.
- [ ] T210 Evaluate suitable Qwen, DeepSeek, Gemma, and Mistral model variants available through the configured provider using representative FLEXCUBE RAG questions. Compare groundedness, correctness, citation compliance, insufficient-information behavior, prompt-injection resistance, latency, hardware requirements, context limits, licensing, and Ollama compatibility. Record results without fabricating results in `docs/evaluation/llm-model-evaluation.md` and the LLM-selection ADR at `docs/adr/ADR-006-llm-selection.md`.
- [x] T204 Complete ADRs for Clean Architecture, FastAPI, frontend architecture, file storage, relational persistence, vector database, LLM adapter, embedding approach, async ingestion, parsing, chunking, hybrid retrieval, reranking, RAG orchestration, degraded mode, sessions, security, and evaluation in `docs/adr/`.
- [x] T205 Add known limitations and pre-production blockers to `docs/architecture/known-limitations.md`, including absent authentication/authorization, Configuration-area access control requirement, no OCR, no containers, no CI/CD, and undecided production topology.
- [x] T206 Run `specs/002-flexcube-support-chatbot/quickstart.md` end-to-end and record any environment-specific deviations in `docs/evaluation/quickstart-validation.md`.
- [x] T207 Run the complete local quality gate: backend unit/API/integration tests available without external services, opt-in Qdrant/Ollama/Oracle tests, `ruff`, strict `mypy`, `tach check`, frontend tests, Playwright tests, and RAG evaluation reporting.
- [x] T208 Review every completed task against `specs/002-flexcube-support-chatbot/spec.md` and `.specify/memory/constitution.md`; record unresolved risks in `docs/architecture/production-readiness-gaps.md`.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 Setup**: T001–T012 can begin immediately; all other phases depend on it.
- **Phase 2 Foundational**: T013–T030 depend on Setup. T013 is a human decision gate; T030 must pass before story work begins.
- **Phase 3 US1**: T031–T045 depend on Phase 2; delivers the MVP document registration slice.
- **Phase 4 US2**: T046–T064 depend on US1's document/job persistence; adds async structured ingestion.
- **Phase 5 US3**: T065–T085 plus moved hybrid tasks T122, T125–T127, T130, T132, and T209 depend on US2's chunks and parser output; T209 also depends on the embedding adapter and vector-index foundation from T072–T074, and model-dependent indexing/evaluation tasks T075, T076, T085, and T132 depend on T209; this phase adds embeddings, index, complete hybrid retrieval, and baseline chat.
- **Phase 6 US4**: T086–T096 depend on US3's chat response path; adds mandatory citation validation/rendering.
- **Phase 7 US5**: T097–T107 depend on US3 and US4; adds evidence sufficiency and explicit unknown handling.
- **Phase 8 US6**: T108–T119 depend on the chat path; adds session-level follow-up behavior.
- **Phase 9 US7**: Remaining T120–T136 depend on US3's completed hybrid retrieval and answer outcomes; adds multi-source behavior and optional reranking evaluation.
- **Phase 10 US8**: T137–T148 depend on document/index lifecycle from US1–US3; applies the confirmed deletion policy and atomic re-indexing.
- **Phase 11 US9**: T149–T159 depend on chat answer identity and session context.
- **Phase 12 US10**: T160–T170 depends on all service adapters and API error handling.
- **Phase 13 US11**: T171–T180 depends on prompt/context and upload paths from US1–US5.
- **Phase 14 US12**: T181–T193 depends on configuration ports and index compatibility from US3/US7.
- **Phase 15 Polish**: T194–T208 depends on all desired story phases; T204 depends on the embedding evaluation and provisional selection in T209 and the LLM evaluation and provisional selection in T210; production readiness remains conditional on open business/security decisions.

### User Story Dependencies

- **US1 (P1)**: Foundational only; MVP document upload and registration.
- **US2 (P1)**: Depends on US1's document registry and job record.
- **US3 (P1)**: Depends on US2's parsed chunks and metadata; implements dense retrieval plus lexical retrieval, exact-identifier matching, metadata filtering, and fusion before chatbot validation.
- **US4 (P1)**: Depends on US3's retrieval and chat response path.
- **US5 (P1)**: Depends on US3's retrieval and US4's response schema.
- **US6 (P2)**: Depends on the chat path; history cannot replace retrieval.
- **US7 (P2)**: Depends on US3's completed hybrid retrieval plus citations and answer outcome models; keeps reranking optional and evidence-based.
- **US8 (P2)**: Uses US1–US3 lifecycle and index capabilities; must follow T013.
- **US9 (P2)**: Depends on chat answers and session context.
- **US10 (P2)**: Cross-cuts all adapters and API behavior; validate after the relevant stories exist.
- **US11 (P1)**: Cross-cuts upload, prompt, response, and API disclosure paths.
- **US12 (P2)**: Depends on configuration persistence, embedding compatibility, and retrieval settings.

### Parallel Opportunities

- Setup tasks T003–T011 can run in parallel after T001/T002 establish the repository.
- Foundational model, port, middleware, and frontend-shell tasks can run in parallel after T001–T002; T030 remains the gate.
- Within each story, tasks marked `[P]` can run concurrently when their listed file sets do not overlap.
- US1 storage, persistence, API tests, and frontend tests can proceed in parallel after the domain ports exist.
- US2 parser adapters, metadata extraction, chunker tests, and status UI can proceed in parallel after `ParsedDocument` contracts are agreed.
- US3 embedding adapter, Qdrant adapter tests, domain models, and frontend chat tests can proceed in parallel after US2 chunks exist.
- US3 exact-identifier extraction, lexical retrieval, hybrid retrieval tests, and retrieval configuration work can proceed in parallel before fusion integration T127; T132 follows the complete hybrid path.
- US10 failure tests, frontend failure-state tests, and security review documentation can proceed in parallel.
- Final ADR and documentation tasks T194–T206 can proceed in parallel; T207/T208 remain final gates.

### Parallel Execution Examples

**US1 after Phase 2 gate**:

```text
T031 upload validation tests
T033 local file-storage integration tests
T034 document API contract tests
T035 document upload frontend tests
T036 persistence mappings
T037 local file-storage adapter
```

**US2 after US1 checkpoint**:

```text
T046 parser contract tests
T047 FLEXCUBE metadata tests
T048 chunking tests
T054 Docling adapter
T055 fallback parser adapters
T056 metadata extractor
T062 status UI
```

**US3 before chatbot validation**:

```text
T122 hybrid retrieval tests
T125 identifier extractor
T126 lexical retriever
T127 fusion and metadata filtering
T130 retrieval configuration API
T132 dense-only versus hybrid baseline
```

**US7 after US5/US6 prerequisites**:

```text
T120 multi-source tests
T121 partial/ambiguous tests
T123 API contract tests
T124 frontend outcome tests
T131 reranker port/adapter
```

---

## Implementation Strategy

### MVP First

1. Complete Phase 1 Setup.
2. Complete Phase 2 Foundational, including the confirmed deletion policy recorded by T013 and all gates.
3. Complete Phase 3 US1.
4. Stop and independently validate upload, validation, registration, and queued status.
5. Do not call the application a chatbot MVP until US2–US5 are complete; US1 is the knowledge-base-management MVP slice.

### First Usable Chatbot Milestone

1. Complete US1 document registration.
2. Complete US2 structured parsing and chunking.
3. Complete US3 embeddings, vector index, hybrid retrieval (dense + lexical + exact
	identifier + metadata filtering + fusion), and Ollama adapter.
4. Complete US4 citation validation.
5. Complete US5 insufficient-information behavior.
6. Validate the thin vertical slice: one FLEXCUBE PDF → asynchronous ingestion → hybrid-ready retrieval → grounded answer → citation or explicit insufficient-information response.

### Incremental Delivery

- Deliver US1 as a standalone Configuration-area increment.
- Add US2 for observable structured ingestion and warning diagnostics.
- Add US3–US5 for the first safe chatbot milestone.
- Add US6–US9 for conversation, multi-source handling, lifecycle consistency, and feedback.
- Add US10–US12 for resilience, security hardening, and runtime configuration.
- Finish with Phase 15 readiness work; do not introduce containers, CI/CD, authentication,
authorization, document versioning, or autonomous system actions.

### Definition of Done for Every Task

A task is complete only when its implementation, focused tests, error handling, privacy/security
checks, documentation, and relevant RAG evaluation are addressed. Compilation alone is not
sufficient. Every completed story must pass its independent test criteria and preserve all
constitutional invariants.
