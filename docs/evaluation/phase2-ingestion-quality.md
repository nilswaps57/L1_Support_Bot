# Phase 2 Ingestion Quality

This document records the evaluation cases for structured ingestion. It intentionally
contains no unmeasured quality claims.

## Fixtures

- Text-based PDF with headings, page breaks, lists, tables, notes, warnings, and procedures.
- DOCX with heading styles, tables, numbered procedures, and FLEXCUBE identifiers.
- Markdown with nested headings, lists, tables, notes, and warnings.
- Corrupt, empty, password-protected, and partially readable files.
- Documents containing task codes, screen names, menu paths, prerequisites, modes, fields,
  procedures, error codes, JIRA IDs, and RCA references.

## Checks

- Every parsed element has a stable type and preserves available page and section metadata.
- Table and procedure elements remain distinguishable from paragraphs.
- Parser warnings identify the affected element and available page without exposing paths,
  credentials, or stack traces.
- Conflicting identifiers remain present in metadata and produce a source-inconsistency
  diagnostic.
- Chunks do not cross section boundaries, preserve table/procedure metadata, obey the
  configured maximum, and apply overlap within a section.
- Prepared documents stop at `READY_FOR_INDEXING` or
  `READY_FOR_INDEXING_WITH_WARNING`; no embedding or vector-index operation is performed.
- `COMPLETED_WITH_WARNING` remains the clarified post-indexing terminal state and is not
  emitted by Phase 4. At this stage, even warning-bearing prepared content is not queryable.
- Worker claims are exclusive, stale active claims are recoverable, retries stop at the
  configured limit, and terminal transitions are not overwritten.

## Observed diagnostics

No benchmark results are recorded yet. Runtime observations should be added here with the
fixture, parser, configuration, warning count, and failure category used to obtain them.
