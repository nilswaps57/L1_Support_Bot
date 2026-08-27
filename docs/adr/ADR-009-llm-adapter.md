# ADR-009: Provider-Independent LLM Adapter

**Status:** Accepted

## Decision

Define an application-owned LLM port and keep Ollama HTTP details in Infrastructure. The adapter
owns timeout, retry, health-check, and safe failure mapping; prompts and evidence policy remain
application concerns.

## Consequences

Ollama is a replaceable local provider, not a production model decision. No provider receives
unframed user instructions or direct vector-store access.
