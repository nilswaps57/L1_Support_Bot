# Architecture Decision Records

This directory contains decisions that affect replaceable infrastructure, application
boundaries, security, and RAG quality. Each ADR records context, options, decision,
rationale, and consequences.

Planned decisions are listed in
[specs/002-flexcube-support-chatbot/plan.md](../../specs/002-flexcube-support-chatbot/plan.md).

The current set includes accepted architecture and boundary decisions, plus explicitly
provisional evidence gates for model selection, reranking, deployment, and licensing. Open
readiness gates must not be converted to accepted decisions without measured evidence.

## Status and traceability matrix

| ADR | Status | Specification / Constitution | Plan / phase | Evidence or open gate |
|---|---|---|---|---|
| ADR-001 | Accepted | Architecture; Principle XXIX | Section 10; Phase 2 | Tach boundary checks |
| ADR-002 | Accepted | API contracts; FR-029 | Sections 4, 12; Phase 2 | FastAPI startup/API tests |
| ADR-003 | Accepted | Frontend route areas; FR-030 | Sections 4, 12; Phase 2 | Vitest, build, Playwright |
| ADR-004 | Accepted for local development | FR-001 to FR-009; Principle IX | Sections 4, 10; Phases 1-3 | File-storage integration tests |
| ADR-005 | Deferred | Principle V; T209 | Sections 5-6; Phases 3-5 | Representative retrieval corpus and candidate endpoints |
| ADR-006 | Provisional | Principles I, IV, VI; T210 | Sections 5-6; Phases 5-7 | Reviewed questions, model comparisons, licence review |
| ADR-007 | Accepted for current scope | FR-007, FR-025, FR-027; Principle X | Sections 4, 7; Phases 1, 8-12 | SQLite tests; Oracle validation pending |
| ADR-008 | Accepted for local development; production deferred | FR-011, FR-012; Principle XV | Sections 4-5; Phases 3-5 | Adapter and in-memory tests; target topology pending |
| ADR-009 | Accepted | FR-013 to FR-015; Principle IV | Sections 4, 10; Phase 5 | Adapter/API tests |
| ADR-010 | Accepted for hybrid retrieval; reranking deferred | FR-015, FR-020; Principles XV-XVII | Sections 5-6; Phases 5, 7 | Existing baseline; T133/T134 remain open |
| ADR-011 | Accepted | FR-005 to FR-010; Principle XII | Sections 4, 10; Phase 4 | Worker and lifecycle tests |
| ADR-012 | Accepted; OCR deferred | FR-002, FR-006; Principle XIII | Sections 7, 10; Phase 4 | Parser tests; licensed-document validation pending |
| ADR-013 | Provisional | FR-010, FR-020; Principle XIV | Sections 5-6; Phases 4-5 | Corpus characterization pending |
| ADR-014 | Accepted | FR-014 to FR-019; Principles I-III | Sections 3, 10; Phases 5-7 | Grounding, citation, and failure tests |
| ADR-015 | Accepted; live validation pending | FR-040; Principle XLVIII | Sections 4, 10; Phase 12 | Deterministic degraded-mode tests |
| ADR-016 | Accepted | FR-021 to FR-024; Principle XXXI | Sections 4, 10; Phase 8 | Session and follow-up tests |
| ADR-017 | Provisional; disabled by default | Principle XVII; T133 | Sections 5-6; Phase 9 | Reviewed reranking experiment pending |
| ADR-018 | Accepted; authorization deferred | FR-031, FR-039; Principles VII-IX, XLVIII | Sections 3, 9; Phases 2, 13 | Security tests; auth/RBAC remains required |
| ADR-019 | Accepted; measurements pending | SC-001 to SC-004; Principle XXXVII | Sections 3, 10; Phase 15 | Synthetic fixtures and metric tests; human review pending |
| ADR-020 | Open readiness gate | Principles IX, X, XLVII | Sections 8-9; Phase 15 | SBOM, licensing, topology, auth, and operations decisions |

Status meanings are deliberate: **Accepted** means the current implementation decision is
supported for its stated scope; **Provisional** means it is usable only as a replaceable
development choice; **Deferred** means no selection is made; and **Open readiness gate** means
deployment approval is explicitly blocked. References to T085, T133, T134, T209, and T210 do
not claim those tasks are complete.
