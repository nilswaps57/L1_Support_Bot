# ADR-019: Evidence-Based RAG Evaluation

**Status:** Accepted, measurements pending

## Decision

Evaluate retrieval and generation on a reviewed, answerability-labelled dataset using frozen
configuration snapshots, deterministic metric calculation, and two independent domain reviewers.
The production candidate LLM cannot be the sole judge of its own output.

## Consequences

Results are reproducible and comparable across providers. Model, embedding, reranking, large-
document, and live-service decisions remain provisional until actual evidence exists.
