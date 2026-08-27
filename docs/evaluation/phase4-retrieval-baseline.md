# Phase 4 Retrieval Baseline

## Status

**Complete for the checked-in synthetic 50-question fixture.** The benchmark result is
stored in `backend/tests/eval/phase4_nomic_results.json` and was produced with
`nomic-embed-text` over fixture `synthetic-flexcube-definitions-v1`.

This is a reproducible pipeline baseline, not a production-quality claim. The fixture is
synthetic, contains 12 labeled chunks derived from `tests/fixtures/flexcube/
sample_definitions.md`, and does not represent the coverage or distribution of a real
FLEXCUBE manual. Real-document validation and broader embedding-model comparison remain
separate pending work.

## Intended comparison

Dense-only and dense-plus-BM25-plus-exact hybrid retrieval were run over the same fixture
using the evaluation script and 50 labeled questions. Reranking was disabled.

| Metric | Dense-only | Hybrid |
|---|---:|---:|
| Recall@5 | 0.96 | 1.00 |
| Recall@10 | 1.00 | 1.00 |
| MRR | 0.8366666667 | 0.84 |
| Exact-identifier hit rate | 0.86 | 0.96 |
| Mean query latency (ms) | 173.7608514 | 202.3284051 |

**Run metadata**:

- Question count: 50
- Chunk count: 12
- Embedding model: `nomic-embed-text`
- Vector dimensions: 768
- Batch embedding latency: 4266.925395 ms
- Fixture: `synthetic-flexcube-definitions-v1`
- Result artifact: `backend/tests/eval/phase4_nomic_results.json`

The hybrid result improves Recall@5 from 0.96 to 1.00 and exact-identifier hit rate from
0.86 to 0.96, while mean query latency increases from approximately 173.76 ms to 202.33
ms on this run. These values are reported for this fixture and environment only.
