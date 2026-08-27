# Post-Phase 5 Task Handoff

Status reconstructed on 2026-08-27 from the previous session transcript, current services, database, and evaluation artifacts.

## Completed

1. **Install and start Qdrant**
   - Qdrant is running in Docker as `l1-support-qdrant`.
   - Health endpoint: `http://localhost:6333/healthz`.
   - Persistent Docker volume: `l1-support-qdrant`.

2. **Install and start Ollama**
   - Ollama is installed and serving on `http://localhost:11434`.
   - Current model listing is available through `/api/tags`.

3. **Pull the development embedding model**
   - `nomic-embed-text` is installed and available.
   - Verified vector size: 768 dimensions.

4. **Pull a small development LLM**
   - `qwen2.5:0.5b` is installed for CPU-friendly development chat checks.
   - `phi3.5` was also installed earlier as the configured development LLM.

5. **Run the synthetic fixture end to end**
   - Synthetic FLEXCUBE fixture was uploaded, parsed, embedded, and indexed.
   - Database result: `COMPLETED_WITH_WARNING`.
   - 12 knowledge chunks were created and 12 were indexed in Qdrant.
   - The warning is expected from intentionally conflicting section-level metadata in the synthetic fixture.

6. **Expand to the 50-question retrieval evaluation**
   - Exactly 50 labeled questions cover the 12 structural chunks.
   - The corrected nomic-embed-text run passed and is stored in `backend/tests/eval/phase4_nomic_results.json`.
   - Recorded metrics:
     - Dense Recall@5: `0.96`
     - Hybrid Recall@5: `1.00`
     - Dense Recall@10: `1.00`
     - Hybrid Recall@10: `1.00`
     - Dense exact-identifier hit rate: `0.86`
     - Hybrid exact-identifier hit rate: `0.96`

## Pending After Phase 5

7. **Evaluate the three embedding candidates**
   - Candidate definitions exist in `backend/tests/eval/embedding_candidates.json`:
     - `qwen3-embedding`
     - `bge-m3`
     - `nomic-embed-text`
   - No complete three-candidate result set is currently recorded.
   - Next actions:
     1. Pull or otherwise make `qwen3-embedding` and `bge-m3` available in Ollama.
     2. Run `backend/scripts/evaluate_embeddings.py` for all three candidates against the 50-question fixture.
     3. Save the three result artifacts under `backend/tests/eval/`.
     4. Compare Recall@5, Recall@10, MRR, exact-identifier hit rate, latency, vector dimensions, and disk/runtime cost.
   - Completion criterion: reproducible result files for all three candidates plus a short comparison report.

8. **Perform the actual PDF and Docling validation**
   - No completed real-PDF validation report is currently stored in the repository.
   - The synthetic Markdown fixture is not evidence for this task.
   - Next actions:
     1. Obtain the permitted Oracle FLEXCUBE Definitions User Manual PDF.
     2. Run `backend/scripts/validate_docling.py` against the real PDF.
     3. Capture parser success/failure, page count, extracted headings, tables, metadata, procedure content, page markers, and diagnostics.
     4. Store the validation output and a concise report under `docs/evaluation/`.
   - Completion criterion: a checked-in report based on the real PDF and Docling output, with any extraction gaps explicitly documented.

## Notes

- The project currently has both a successful synthetic ingestion job and an older queued/failed job referring to a missing source document. The successful synthetic job is the evidence for task 5.
- Local runtime state such as SQLite databases, Docker volumes, Ollama models, and generated service data is intentionally excluded from Git by the root `.gitignore`.
- This handoff file is a planning record. It does not claim that tasks 7 or 8 are complete.
