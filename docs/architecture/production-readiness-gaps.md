# Production Readiness Gaps

**Review date:** 2026-08-27
**Current classification:** Engineering prototype
**Production status:** Not production ready

This review compares the implementation with [spec.md](../../specs/002-flexcube-support-chatbot/spec.md),
[plan.md](../../specs/002-flexcube-support-chatbot/plan.md), the Constitution, API contracts,
data model, ADRs, and evaluation reports. Local deterministic evidence is not treated as live
FLEXCUBE or production evidence.

## Implementation-complete capabilities

- Document validation, UUID-backed file storage, checksum duplicate detection, and safe cleanup.
- Structured parsing adapters, metadata extraction, structure-aware chunking, persistent jobs,
  retry handling, warning states, and failure diagnostics.
- Configurable embeddings, Qdrant adapter, exact-identifier retrieval, lexical retrieval,
  dense-plus-sparse fusion, evidence sufficiency, citation validation, and grounded prompting.
- Insufficient, partial, ambiguous, session follow-up, multi-source, feedback, deletion, and
  atomic re-indexing behavior.
- Safe LLM, vector, embedding, database, parser, and degraded-mode error boundaries.
- Prompt-injection resistance, disclosure filtering, transactional configuration, and the React
  Configuration and Chat UI areas.

## Deterministically validated capabilities

- Backend unit/API/integration tests, parser and lifecycle regressions, migration checks, Ruff,
  strict mypy, and Tach boundary checks pass in the recorded local environment.
- Frontend component tests, production build, accessibility checks, deterministic workflow E2E,
  failure/security E2E, and responsive UI checks pass.
- Synthetic RAG cases, metric calculations, configuration snapshots, and append-only evaluation
  persistence are validated without claiming model quality.
- The quickstart validation records the exact environment deviations and does not claim a clean
  machine or production deployment result.

## Live-service validated capabilities

- Local Qdrant health endpoint reachability was observed.
- Local Ollama API reachability and the installed development inventory were observed.
- These are service reachability observations only. No live FLEXCUBE ingestion, indexed answer,
  citation traceability, Oracle recovery, or provider outage result is claimed.

## Not externally validated

- Real approved FLEXCUBE PDF/Docling parsing, large-document memory behavior, indexing, retrieval,
  generation, and citation correctness.
- Live embedding-provider behavior, Qdrant production operation, Ollama model behavior, and
  Oracle degraded-mode recovery.
- Two qualified human reviewers, adjudication, live prompt-injection assessment, and full
  accessibility/screen-reader certification.
- Vulnerability certification, complete SBOM/licence review, capacity, backup, retention,
  monitoring, failover, and disaster recovery.

## Deferred tasks

- T085: independent real-document US3 validation.
- T133/T134: reranking experiment and evidence-based reranking ADR decisions.
- T209: embedding candidate evaluation and selection.
- T210: LLM candidate evaluation and selection.

All remain unchecked. T132 and T194-T203 remain complete. No unmeasured model, embedding, or
reranking choice is presented as final.

## Security blockers

- Authentication is absent.
- Authorization, RBAC, SSO, and Configuration-area access control are absent; current access is
  unrestricted.
- Human adversarial review, live model injection review, dependency vulnerability certification,
  secret scanning, and transitive SBOM/licence review remain pending.
- PyMuPDF licensing requires a commercial, replacement, or legal approval decision.

## Deployment blockers

- Production topology, mandatory deployment architecture, HA/failover, capacity, backup,
  retention, monitoring, alerting, operational ownership, and recovery runbooks are undecided.
- CI/CD, release controls, rollback, and environment promotion are absent.
- Local Qdrant Docker use is temporary development support, not a production architecture.
- OCR for scanned PDFs is unavailable, and behavior is English-only.
- Session history is bounded to active in-memory sessions.

## Data-governance decisions required

- Classify uploaded documents, queries, retrieved context, feedback, embeddings, and logs.
- Approve retention, deletion, backup, residency, access auditing, and Oracle data-handling rules.
- Decide whether external embedding services and model downloads are permitted and under what
  egress controls.
- Define ownership for the knowledge base, incident response, and evidence review.

## Model-selection decisions required

- Provide an approved representative corpus and reviewed questions.
- Evaluate embedding candidates with retrieval metrics, dimensions, storage, latency, licensing,
  and deployment feasibility before T209 can close.
- Evaluate LLM candidates for correctness, groundedness, citations, insufficient-information
  handling, injection resistance, latency, context, hardware, licensing, and compatibility before
  T210 can close.
- Evaluate reranking quality versus cost before enabling it.

## Recommended next milestone

Run a controlled evidence milestone using an approved FLEXCUBE document, reviewed 100-case
question set, approved candidate endpoints/models, two qualified reviewers, and an isolated test
environment. Preserve only non-copyrighted metrics and configuration snapshots, then revisit
T085, T133, T134, T209, and T210. After those gates, address authentication, authorization,
topology, governance, licensing, and operational controls before any production decision.
