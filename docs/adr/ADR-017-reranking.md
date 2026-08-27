# ADR-017: Optional Reranking

## Context

Reranking may improve ordering of hybrid retrieval candidates, but it can add latency,
resource use, and a model licensing/runtime dependency. The application needs to preserve a
replaceable boundary while avoiding an unmeasured production default.

## Provisional Decision

Expose reranking through `RerankerPort` with a lazy FlashRank adapter. Invoke it only when
`RetrievalConfig.rerank_enabled` is explicitly true and an adapter is installed. Keep the
default disabled.

## Evaluation Status

The required 100-question reviewed dataset and locally available FlashRank model are absent,
so no experiment measurements are claimed. The no-rerank versus rerank decision remains
unchecked and provisional. See [phase7-reranking.md](../evaluation/phase7-reranking.md).