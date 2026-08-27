# Document Index Consistency

## Deletion

Deletion is allowed only for `COMPLETED`, `COMPLETED_WITH_WARNING`, and `FAILED`
documents. Any active ingestion state, including `QUEUED`, returns
`DOCUMENT_IN_PROCESSING`; the ingestion job is not changed. A document in
`DELETING` is a retry of the same cleanup operation, and `DELETED` is idempotent.

Cleanup has a fixed order:

1. Delete all document points from the active and known staging Qdrant collections.
2. Delete relational knowledge chunks.
3. Delete ingestion diagnostics.
4. Delete ingestion job records.
5. Delete the locally stored source file.
6. Persist the document tombstone as `DELETED`.

The first step makes the document unavailable to retrieval before metadata and source
cleanup. Every operation is document-scoped and idempotent. A failure leaves the
tombstone in `DELETING`, returns `DOCUMENT_CLEANUP_FAILED`, and never reports successful
delete completion. A later request repeats cleanup from the failed boundary. The document
row is retained as a tombstone so citation validation and repeated requests remain
deterministic.

## Re-indexing

Re-indexing is allowed for `COMPLETED`, `COMPLETED_WITH_WARNING`, and `FAILED` documents.
The existing document status and active generation remain usable while the replacement is
built. A replacement job records the embedding model identity and a deterministic chunking
configuration snapshot.

The Qdrant index manager:

1. Creates a uniquely named staging collection.
2. Copies every active point except the document being replaced into staging.
3. Embeds and writes the replacement chunks to staging.
4. Validates point count, document ownership, and embedding-model compatibility.
5. Changes the active collection under a lock in one cutover operation.
6. Replaces relational chunks with the staged generation.
7. Removes the superseded collection only after the new generation is active.

If parsing, embedding, staging, validation, or relational replacement fails, the active
collection remains unchanged; failed staging is removed. If relational replacement fails
after cutover, the manager rolls back to the previous generation before removing staging.
A post-cutover superseded-collection cleanup failure is reported as a failed job while the
new generation remains active; retrying cleanup is safe and does not expose mixed chunks.

Retrieval captures the active collection name before issuing a search. Therefore a query
uses one complete collection generation even when cutover happens concurrently. No search
reads staging collections. Each replacement chunk stores its generation ID, embedding
model ID, and source metadata, while the ingestion job stores the chunking snapshot.

## Retrieval and citations

`AskQuestion` still filters retrieved chunks through the document registry's queryable
status. A deleted tombstone is not queryable, and deletion removes its vectors from all
known collections. Consequently deleted content cannot contribute to a new answer or
citation. A replacement generation contains either the complete old-document exclusion
plus the complete replacement document, so old and new chunks are never returned together.

The manager's active-generation pointer is process-local. A multi-process deployment must
persist or use a Qdrant alias for the pointer before being treated as production-ready;
the current laptop runtime and concurrent-request contract are protected by the manager
lock.
