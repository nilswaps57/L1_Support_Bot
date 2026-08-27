# ADR-011: Persistent Asynchronous Ingestion

**Status:** Accepted

## Decision

Use a poll-based worker and SQLAlchemy ingestion-job table. Claims, retries, recovery, terminal
states, warnings, and index completion are persisted. No broker or container is required.

## Consequences

Uploads return promptly and progress is observable. Throughput and multi-worker scaling require
future capacity work; failed jobs expose safe diagnostics rather than disappearing.
