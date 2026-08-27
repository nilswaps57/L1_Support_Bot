# ADR-015: Explicit Read-Only Degraded Mode

**Status:** Accepted, live outage validation pending

## Decision

When relational metadata is unavailable but cached runtime configuration, Qdrant, embedding, and
LLM remain usable, allow indexed read-only answering where technically feasible. Block uploads,
deletes, re-indexing, feedback, and configuration mutations. Surface a degraded health state.

## Consequences

Users receive explicit capability limits instead of fabricated answers. Recovery and Oracle
behavior require safe live validation; this is not an availability guarantee.
