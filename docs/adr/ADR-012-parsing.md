# ADR-012: Structure-Preserving Parsing

**Status:** Accepted, OCR deferred

## Decision

Use Docling as the primary parser with PyMuPDF and python-docx fallbacks. Preserve pages,
headings, lists, tables, procedures, warnings, and FLEXCUBE metadata; treat source instructions
as passive text. Scanned-document OCR is outside this phase.

## Consequences

Chunking and citations retain source structure. Real PDF quality, table fidelity, and OCR needs
must be measured with an approved manual before T085 can close.
