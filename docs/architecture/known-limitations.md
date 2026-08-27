# Known Limitations and Pre-Production Blockers

**Review date:** 2026-08-27
**Readiness classification:** Engineering prototype; not production ready

This document separates implementation limits from evidence and governance gates. A listed
capability must not be treated as production-ready merely because deterministic tests pass.

## Production blockers

| Blocker | Current state | Required closure |
|---|---|---|
| Authentication | No authentication | Implement and review identity integration |
| Authorization/RBAC | No authorization or RBAC | Restrict document and configuration operations |
| SSO | No SSO | Select and approve the organizational identity path |
| Configuration access | Configuration area is unrestricted in the current build | Enforce role-based access before deployment |
| Production topology | No topology, capacity, backup, retention, or ownership decision | Approve the target operating model |
| Deployment architecture | No mandatory container deployment architecture | Decide and validate the supported topology |
| CI/CD | No CI/CD pipeline | Establish controlled build, test, release, and rollback processes |
| High availability | No HA, failover, or disaster-recovery design | Define availability and recovery objectives and test them |
| Production LLM | No finalized production LLM | Complete T210 and licence/hardware review |
| Production embedding | No finalized production embedding model | Complete T209 against a representative corpus |
| Real-document validation | Real FLEXCUBE PDF and live Docling validation pending | Use an approved, non-committed document fixture |
| Reranking | Reranking evaluation pending | Complete T133/T134 before enabling it |
| Live outage validation | Live Qdrant, Ollama, embedding, and Oracle outage/recovery checks pending | Test in the target environment |
| Vulnerability certification | Backend advisory scan and SBOM/licence certification pending | Run approved scanners and close or accept findings |
| Human adversarial review | Two qualified reviewers and adjudication are pending | Review the RAG, injection, citation, and disclosure cases |
| Accessibility certification | Full accessibility and screen-reader certification pending | Complete manual WCAG-oriented review |

## Controlled proof-of-concept limitations

| Limitation | Boundary and control |
|---|---|
| English-only behavior | Multilingual retrieval and generation are not validated |
| No OCR | Scanned PDFs are not supported; parser OCR extension remains unselected |
| In-memory sessions | History is limited to active, bounded in-memory sessions and expires |
| Local Qdrant operation | Standalone Qdrant is the supported development default; temporary Docker Qdrant is allowed only for local development |
| Local filesystem storage | UUID-backed files are suitable for local development; durable production storage is undecided |
| Application logging only | No production metrics, tracing, alerting, or centralized audit platform is selected |

## Deferred enhancements

- Document versioning and long-term user profiles remain out of scope.
- Autonomous actions, FLEXCUBE mutations, SQL execution, and JIRA modification remain
   prohibited by the safety boundary.
- OCR, persistent chat history, and richer observability require separate approved scope.

## Operational decisions required

- Data classification, retention, deletion, backup, restore, and residency policy for uploaded
   documents, queries, retrieved context, feedback, and embeddings.
- Approved external-egress policy for embedding providers and model downloads.
- Supported Python/Node/Qdrant/Ollama versions, capacity envelope, ownership, alerting, and
   recovery runbooks.
- Dependency licensing decision for PyMuPDF and exact locked transitive dependencies.

The application is not production ready while any production blocker above remains unresolved.
This phase introduces none of authentication, authorization, mandatory containers, CI/CD, HA,
or a production topology.
