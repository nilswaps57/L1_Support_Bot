# ADR-010: Hybrid Retrieval Decision

**Status:** Accepted for hybrid retrieval; reranking deferred

## Context

FLEXCUBE questions include natural-language descriptions and exact identifiers such as task
codes and error codes. A useful answer may require related chunks from more than one source.
The Phase 5 hybrid retrieval implementation and baseline evaluation are already complete.

## Decision

Retain dense, lexical, and exact-identifier retrieval behind the existing retriever port.
Fuse and deduplicate candidates before evidence assessment. Exact identifier hits are
prioritized, while relevant companion evidence may remain available for cross-source
answers. Reranking is an optional later stage and remains disabled by default pending the
reviewed Phase 7 experiment.

## Consequences

The answer generator receives a bounded, deduplicated evidence set that can contain multiple
documents. Citation validation still requires explicit model-selected chunk identities, so a
retrieved document is never cited merely because it was returned by search.

The hybrid behavior itself is not re-evaluated here; its existing Phase 5 regression and
baseline artifacts remain the source of truth. The reranking decision remains open because
the reviewed evaluation dataset and local model are unavailable.