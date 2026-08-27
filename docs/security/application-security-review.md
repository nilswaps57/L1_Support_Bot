# OWASP-Oriented Application Security Review

**Review date:** 2026-08-27
**Scope:** local Phase 15 review of the upload, API, RAG, persistence, and frontend boundaries

This is a design and test review, not a penetration test or production-grade attack-resistance
claim. Authentication and Configuration-area authorization are intentionally out of scope and
remain deployment blockers.

## Review checklist

| Area | Control reviewed | Evidence/status |
|---|---|---|
| Uploads | Extension, MIME, magic-byte, empty-file, size, checksum, and multipart validation | Implemented and covered by US1 tests; live licensed-document validation remains pending |
| Path traversal | UUID-backed storage names, resolved-path containment, atomic writes, cleanup | Implemented and covered by file-storage tests |
| Malicious documents | Parsers receive bytes as passive data; no macros, links, shell commands, or embedded instructions are executed | Deterministic parser/storage tests pass; adversarial human review pending |
| CORS | Allowed origins are configured, not wildcarded by default | Implemented; deployment values require review |
| Input handling | Pydantic/API validation, bounded request bodies, bounded session history, query normalization | Implemented and covered by API/application tests |
| Output handling | Response disclosure validation removes prompt, secret, path, endpoint, SQL, and stack-trace disclosures | Implemented and covered by security tests |
| Secrets | Settings load from environment; masked configuration DTOs; no secret logging | Implemented; secret scanning still required in release infrastructure |
| Prompt injection | User queries and retrieved documents are framed as untrusted reference material; refusal and grounding paths exist | Deterministic tests pass; live-model assessment pending |
| Error disclosure | Domain errors map to safe categories and request IDs; infrastructure details are not returned | Implemented and covered by API tests |
| Retrieval integrity | Evidence sufficiency and citation membership checks prevent unsupported citations | Implemented; real-corpus validation pending |
| Persistence | Upload, deletion, re-indexing, and configuration activation preserve transactional/atomic behavior | Implemented and covered by lifecycle/configuration tests |
| Availability | Qdrant, Ollama, embedding, and database failures map to explicit safe failure or degraded mode | Deterministic tests exist; live outage checks pending |
| Authorization | Authentication and access control for Configuration operations | **BLOCKER:** not implemented by scope decision |

## Required adversarial review

Two independent reviewers with FLEXCUBE L1 support or security expertise must review the 100-case
RAG set, injection cases, citation behavior, and disclosure controls. Disagreements require
adjudication. Deterministic tests alone do not establish production attack resistance.

## Phase 15 disposition

- No new tool execution, SQL execution, FLEXCUBE mutation, JIRA mutation, authentication, or
  authorization capability is introduced.
- Live-model injection and false-positive cases cannot be claimed complete until the evaluated
  model set and representative reviewed corpus are available.
- Ordinary UI presentation must continue to exclude secrets, internal identifiers, endpoints,
  configuration details, SQL, and stack traces.
