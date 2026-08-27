# Research: FLEXCUBE L1 Support Chatbot — Phase 0 Resolved Unknowns

**Feature**: 002-flexcube-support-chatbot
**Date**: 2026-08-26

---

## 1. Python API Framework

**Decision**: FastAPI

**Rationale**: Native OpenAPI 3.x generation from Pydantic models satisfies the REST/OpenAPI
requirement. Async-first, Pydantic v2 validation at all boundaries, clean router separation
from business logic. Well-established for RAG backends.

**Alternatives considered**: Flask (no native OpenAPI, synchronous), Django REST Framework
(ORM-coupled, harder to enforce Clean Architecture), Litestar (strong but smaller community).

---

## 2. Vector Database

**Decision**: Qdrant (primary); LanceDB (embedded fallback)

**Rationale**: Qdrant is Apache 2.0, runs as a standalone binary with no Docker required,
provides native dense + sparse hybrid search, first-class payload filtering for exact
identifiers, and strong Python SDK. LanceDB provides a zero-install fallback for environments
where the Qdrant binary cannot run.

**Alternatives ruled out**: pgvector (requires PostgreSQL alongside Oracle — too complex),
Milvus/Weaviate (Docker-first), ChromaDB (limited sparse search).

---

## 3. Relational Persistence

**Decision**: SQLAlchemy 2.x (async) + Alembic; Oracle (production), SQLite (dev/degraded)

**Rationale**: Identical interface across both dialects via `DATABASE_URL` env var.
Oracle thin mode (`python-oracledb`) avoids Instant Client requirement on many versions.
SQLite (`aiosqlite`) is zero-install and always available.

---

## 4. Document Processing

**Decision**: Docling (primary, all formats); PyMuPDF/pymupdf4llm (PDF fallback);
python-docx (DOCX supplement)

**Rationale**: Docling v2 produces structured JSON output preserving tables, headings,
page numbers, and section hierarchy — critical for FLEXCUBE manuals. PyMuPDF is a
reliable fast fallback for simpler PDFs. python-docx handles DOCX edge cases.

**OCR**: Out of scope for initial release. `DocumentParser` port includes
`ParseCapability.requires_ocr` flag for future routing.

---

## 5. Asynchronous Ingestion

**Decision**: Poll-based worker + SQLAlchemy `ingestion_jobs` table

**Rationale**: No external broker, no containers, persistent job state, recoverable after
crash. Worker polls every 2 seconds; claims jobs atomically (`UPDATE ... RETURNING`).
Future migration to Celery + Redis requires only a `JobQueuePort` adapter swap.

---

## 6. Lexical Retrieval

**Decision**: Qdrant sparse vectors (BM25-weighted) + regex-based exact-identifier extraction

**Rationale**: BM25 sparse vectors stored alongside dense vectors in the same Qdrant
collection. Exact identifiers (task codes, error codes, JIRA IDs) bypass BM25 and use
Qdrant payload filters directly — guaranteeing exact-match retrieval without semantic
degradation. `rank_bm25` used to compute term weights client-side.

---

## 7. RAG Framework

**Decision**: Custom orchestration — no external RAG framework

**Rationale**: LangChain, LlamaIndex, and Haystack all impose abstractions that conflict
with Clean Architecture. The RAG pipeline is tractable (15 stages) and better served by
explicit code behind ports. Full transparency and testability preserved.

---

## 8. Reranking

**Decision (provisional)**: FlashRank (`ms-marco-MiniLM-L-4-v2`) as candidate reranker;
disabled by default; Phase 7 A/B evaluation governs enable/disable

**Rationale**: CPU-compatible, Apache 2.0, pip installable, no GPU or external API
required. Suitable for the developer laptop constraint.

---

## 9. Development LLM (provisional)

**Decision**: `phi3.5` or `qwen2.5:7b` via Ollama

**Rationale**: Lightweight CPU-compatible quantised models for pipeline validation.
NOT the production decision. Model swapped via `OLLAMA_MODEL` env var.

---

## 10. Development Embedding (provisional)

**Decision**: `nomic-embed-text` via Ollama `/v1/embeddings` endpoint

**Rationale**: Zero external API dependency during development. Production embedding
model selected via Phase 3–4 evaluation (candidates: Qwen3-Embedding, BGE-M3).

---

## 11. Frontend State

**Decision**: TanStack Query v5 (server state); React hooks (UI state); React Hook Form
(forms); no global state library

**Rationale**: Sufficient for application complexity. No Zustand/Redux justified yet.

---

## 12. Backend Engineering Tools

| Tool | Purpose |
|---|---|
| uv | Fast Python package manager (replaces pip + venv) |
| ruff | Linter + formatter (replaces flake8, black, isort) |
| mypy --strict | Static type checking |
| tach | Architecture boundary enforcement (Clean Architecture) |
| pytest + pytest-asyncio | Testing |
| pytest-cov | Coverage reporting |

---

ingestion state machine in plan.md Section 19 requires updating.
## 13. Confirmed Deletion Policy (Q2)

When deletion is requested while ingestion is active, deletion is blocked. The API
returns the safe conflict category `DOCUMENT_IN_PROCESSING`, and the active ingestion
job continues unchanged. Deletion may be retried after the document reaches a terminal
state. Cancellation and queued deletion are not supported by this feature.
