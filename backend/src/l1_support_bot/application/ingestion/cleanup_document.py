"""Ordered, retryable cleanup for a document and all indexed artifacts."""

from l1_support_bot.domain.errors import CleanupFailedError
from l1_support_bot.domain.models.document import Document
from l1_support_bot.domain.models.ingestion import IngestionStatus
from l1_support_bot.domain.ports.file_storage import FileStoragePort
from l1_support_bot.domain.ports.repositories import (
    ChunkRepository,
    DiagnosticRepository,
    DocumentRepository,
    IngestionJobRepository,
)
from l1_support_bot.domain.ports.vector_store import VectorStorePort


class CleanupDocument:
    """Remove retrieval artifacts first, retaining a tombstone for safe retries."""

    def __init__(
        self,
        *,
        documents: DocumentRepository,
        jobs: IngestionJobRepository,
        chunks: ChunkRepository,
        diagnostics: DiagnosticRepository,
        vectors: VectorStorePort,
        storage: FileStoragePort,
    ) -> None:
        self.documents = documents
        self.jobs = jobs
        self.chunks = chunks
        self.diagnostics = diagnostics
        self.vectors = vectors
        self.storage = storage

    async def execute(self, document: Document) -> Document:
        if document.status is IngestionStatus.DELETED:
            return document
        deleting = document
        if document.status is not IngestionStatus.DELETING:
            deleting = document.transition_to(IngestionStatus.DELETING)
            await self.documents.save(deleting)
        try:
            # Retrieval is disabled before metadata and source cleanup can begin.
            await self.vectors.delete_by_document(deleting.id)
            await self.chunks.delete_by_document(deleting.id)
            await self.diagnostics.delete_diagnostics_by_document(deleting.id)
            await self.jobs.delete_by_document(deleting.id)
            await self.storage.delete(deleting.storage_path)
            deleted = deleting.transition_to(IngestionStatus.DELETED)
            return await self.documents.save(deleted)
        except Exception as exc:
            raise CleanupFailedError(
                "The document cleanup did not complete. The document remains unavailable "
                "until cleanup is retried."
            ) from exc


async def cleanup_document(
    document: Document,
    *,
    documents: DocumentRepository,
    jobs: IngestionJobRepository,
    chunks: ChunkRepository,
    diagnostics: DiagnosticRepository,
    vectors: VectorStorePort,
    storage: FileStoragePort,
) -> Document:
    return await CleanupDocument(
        documents=documents,
        jobs=jobs,
        chunks=chunks,
        diagnostics=diagnostics,
        vectors=vectors,
        storage=storage,
    ).execute(document)
