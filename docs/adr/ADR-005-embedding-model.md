# ADR-005: Embedding Model Selection

## Status

Evaluation blocked pending representative FLEXCUBE retrieval fixtures and reachable candidate
embedding endpoints.

## Decision

No provisional embedding model is selected in Phase 5. The implementation tracks provider,
model, version, dimensions, and index compatibility through `EmbeddingConfig` and each vector
payload. The T209 harness records measured candidate results when actual fixtures and endpoints
are supplied.

## Consequences

- No fabricated retrieval metrics are introduced.
- Qdrant indexes reject incompatible embedding identities before indexing.
- A model selection decision remains required before production adoption.
