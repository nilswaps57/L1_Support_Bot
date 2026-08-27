# ADR-002: FastAPI REST Boundary

**Status:** Accepted

## Decision

Use FastAPI as the versioned REST interface, with Pydantic DTO validation, explicit middleware,
and router-level error translation. The interface invokes application use cases and contains no
retrieval or provider policy.

## Consequences

OpenAPI and async request handling are available locally. Authentication and authorization remain
extension points and production blockers rather than being implied by the framework.
