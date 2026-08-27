# ADR-018: Security and Safety Boundary

**Status:** Accepted, production authorization pending

## Decision

Treat user input and documents as untrusted; validate uploads, sanitize queries, frame context as
reference material, validate disclosures and citations, and expose no tool execution, SQL, JIRA,
FLEXCUBE mutation, secrets, prompts, paths, or stack traces. Authentication and Configuration-area
authorization are future boundary requirements.

## Consequences

Deterministic controls are testable and safe by default. They do not prove production attack
resistance; two-reviewer and live-model adversarial assessment remain required.
