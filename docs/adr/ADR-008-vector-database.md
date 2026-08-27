# ADR-008: Qdrant Vector Database

**Status:** Accepted for local development and provisional deployment

## Decision

Use Qdrant behind the vector-store port, running as a standalone local binary. Store embedding
identity and source metadata with vectors, and reject incompatible indexes before use.

## Consequences

Dense, sparse, exact-identifier, and payload-filter retrieval can share one adapter. Docker is
not required and is intentionally not introduced. Production capacity, persistence, backup, and
access control remain open deployment decisions.
