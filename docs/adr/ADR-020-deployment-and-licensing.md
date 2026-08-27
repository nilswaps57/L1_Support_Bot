# ADR-020: Deployment and Licensing Gate

**Status:** Open readiness gate

## Decision

Keep Docker, CI/CD, authentication, authorization, and production topology out of Phase 15 as
specified. Treat them as explicit deployment work, not hidden assumptions. Use standalone Qdrant
as a temporary local-development choice while the production topology is undecided.

## Licensing gate

A release requires an SBOM/licence review and a decision on PyMuPDF's AGPL-3.0 or commercial
terms. No distribution approval is implied by the current local dependency set.
