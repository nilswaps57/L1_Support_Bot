# Embedding Model Evaluation

## Scope

T209 requires measurements on representative FLEXCUBE retrieval fixtures for Qwen3-Embedding,
BGE-M3, and `nomic-embed-text`. The executable harness is
`backend/scripts/evaluate_embeddings.py`. It reports Recall@5, Recall@10, MRR,
exact-identifier hit rate, batch/query latency, vector dimensions, estimated vector storage,
and candidate licensing/deployment metadata.

## Current Result

**Blocked: no representative FLEXCUBE retrieval fixture or embedding endpoints are available
in this workspace.** The repository contains only synthetic BA435 unit-test data, which is not
used as a T209 benchmark. No candidate result is reported and no provisional model is selected.

Run with externally supplied actual fixture and candidate endpoint configuration:

```bash
cd backend
uv run python scripts/evaluate_embeddings.py /path/to/flexcube-fixture.json candidates.json \
  --output /path/to/embedding-results.json
```

Candidate results must be copied from the command output into this document with the fixture
identity, date, endpoint/model version, and observed metrics. Do not substitute generic model
benchmarks or synthetic fixtures.
