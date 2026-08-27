# ADR-007: Relational Persistence

**Status:** Accepted for the current scope

## Decision

Use SQLAlchemy 2.x with Alembic, Oracle as the intended production relational target, and
SQLite/aiosqlite for local development and degraded-mode support. Repositories implement domain
ports and migrations remain linear with one head.

## Consequences

Metadata, jobs, feedback, configuration, and evaluation snapshots share transaction semantics.
Oracle connectivity and production schema behavior require an opt-in environment validation.
