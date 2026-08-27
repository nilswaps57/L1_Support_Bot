# ADR-013: Structure-Aware Chunking

**Status:** Provisional, corpus evaluation pending

## Decision

Chunk by section while keeping tables, lists, and procedures as atomic structures where possible.
Use configurable starting values of 512 target tokens, 1024 maximum tokens, and 64-token overlap.

## Consequences

Metadata and citation locations survive chunking, and values can be tuned without changing ports.
The starting values are not performance targets and must be evaluated on a representative manual.
