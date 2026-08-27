# ADR-014: Explicit RAG Orchestration

**Status:** Accepted

## Decision

Use explicit application orchestration for query sanitization, fresh retrieval, evidence sufficiency,
context assembly, grounded prompt construction, generation, citation construction, and response
validation. Do not add LangChain, LlamaIndex, or direct model/vector coupling.

## Consequences

Every stage is testable and replaceable, and conversation history cannot substitute for evidence.
Evaluation runs use the same ports and configuration snapshots as normal requests.
