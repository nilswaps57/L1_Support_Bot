# ADR-003: React Frontend Architecture

**Status:** Accepted

## Decision

Use one Vite React/TypeScript SPA with separate `/chat` and `/config/*` route areas. TanStack
Query owns server state, React hooks own local UI state, and forms use React Hook Form. The
frontend consumes versioned API DTOs and keeps secrets and infrastructure details out of views.

## Consequences

The UI remains replaceable from backend internals and supports explicit loading, degraded, error,
and citation states. Authentication can be added at the route boundary later.
