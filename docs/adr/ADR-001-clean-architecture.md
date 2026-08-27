# ADR-001: Clean Architecture

**Status:** Accepted

## Context

Grounding, citation, and failure controls must remain independent of replaceable providers.

## Decision

Use `Interface -> Application -> Domain <- Infrastructure`. Ports are owned by Domain;
use cases are owned by Application; FastAPI and provider/database adapters stay at the edges.
Tach checks the import direction.

## Consequences

Providers can change without rewriting use cases. Cross-layer convenience imports are rejected,
and evaluation code must use the same boundaries.
