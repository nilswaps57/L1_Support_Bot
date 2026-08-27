# Citation Traceability

Phase 6 keeps every displayed source tied to the retrieval set for the current question.
The trace is:

```text
source document
  -> parsed element and preserved metadata
  -> knowledge chunk (chunk_id)
  -> retrieval result for the current question
  -> framed context passed to the LLM
  -> supported_chunk_ids selected by the answer
  -> validated Citation
  -> API CitationResponse
  -> frontend CitationItem
```

## Construction

The LLM response must provide `supported_chunk_ids`. `CitationBuilder` resolves those IDs
against the current retrieved results and copies source metadata from the matched chunk. A
retrieved result is not cited merely because it passed the retrieval threshold; it must be
explicitly selected as materially supporting the answer. Duplicate IDs, malformed IDs, IDs
not retrieved for the current question, and IDs from unavailable documents are rejected.

`ResponseValidator` repeats the source-membership check at the answer boundary. It also
checks that the citation document identity and every preserved metadata field match the
retrieved chunk. This prevents a generated response from replacing source metadata with
invented values.

## Availability And Response Types

The application resolves each retrieved document through `DocumentRepository` and retains
only documents in a queryable terminal state (`COMPLETED` or `COMPLETED_WITH_WARNING`).
Deleted, missing, processing, and otherwise unavailable documents therefore cannot reach
the citation builder. Supported (`GROUNDED` and `PARTIAL`) answers require at least one
validated citation. Insufficient and ambiguous responses contain no citations.

The API omits optional source-location fields when the chunk has no corresponding metadata.
In particular, a missing page number is not replaced with a guessed or synthetic value.

Synthetic source-page markers used in deterministic fixtures validate metadata propagation
only. They do not validate page-number extraction from an actual PDF. PDF extraction quality
remains the responsibility of the parser and its integration tests.

## Frontend

`CitationList` renders one accessible source list for a response. Each `CitationItem` shows
the document name, chunk identity, and any available page, section, task, screen, error, or
JIRA metadata. Conditional rendering keeps unavailable locations absent from the interface.
The chat message model carries citations from the API; insufficient or error messages do
not render the source list.