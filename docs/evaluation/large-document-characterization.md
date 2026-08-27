# Large-Document Characterization

**Status:** protocol added; live FLEXCUBE measurements pending
**Review date:** 2026-08-27

## Scope and data handling

Use one locally stored, Git-ignored representative FLEXCUBE manual. Do not commit, copy, or
reproduce licensed document content. The test fixture at
`backend/tests/integration/parsing/test_large_documents.py` generates a synthetic structure for
regression and memory-shape checks; it is not a substitute for the licensed manual.

## Measurements to record

For the same document and configuration snapshot, record:

- file size and page count (metadata only)
- parser and Docling version
- parsing wall time and warnings
- element and chunk counts
- embedding wall time, batch size, and vector dimensions
- indexing wall time and indexed count
- peak process memory or an explicitly unavailable measurement
- retrieval latency for the reviewed question set
- LLM latency and model/context configuration
- failures, retries, degraded-mode transitions, and recovery observations

No performance targets are invented here. Results should include the machine, operating system,
Python version, model versions, Qdrant mode, and timestamp so a later comparison is meaningful.

## Execution protocol

1. Place the approved PDF outside tracked paths, under a Git-ignored local validation directory.
2. Run `uv run python scripts/validate_docling.py /path/to/manual.pdf` and retain only metrics,
   warnings, and non-copyrighted observations.
3. Run the normal ingestion worker with a configuration snapshot.
4. Capture the timings above without storing document text or generated answers in the repository.
5. Exercise retrieval and generation using the reviewed RAG cases.
6. Repeat safe outage checks for Qdrant, Ollama, the embedding endpoint, and Oracle, then verify
   recovery and read-only degraded behavior.

## Current result

No licensed FLEXCUBE PDF is present in this workspace, so no real parsing, chunking, embedding,
indexing, retrieval, generation, memory, or outage result is claimed. T085 remains incomplete.
