"""Delete a document only after ingestion reaches an approved terminal state."""

from typing import Protocol
from uuid import UUID

from l1_support_bot.domain.errors import DocumentInProcessingError, DocumentNotDeletableError
from l1_support_bot.domain.models.document import Document
from l1_support_bot.domain.models.ingestion import IngestionStatus
from l1_support_bot.domain.ports.repositories import DocumentRepository

_APPROVED_STATES = frozenset(
    {
        IngestionStatus.COMPLETED,
        IngestionStatus.COMPLETED_WITH_WARNING,
        IngestionStatus.FAILED,
    }
)


class DocumentCleanup(Protocol):
    async def execute(self, document: Document) -> Document: ...


class DeleteDocument:
    def __init__(self, *, documents: DocumentRepository, cleanup: DocumentCleanup) -> None:
        self.documents = documents
        self.cleanup = cleanup

    async def execute(self, document_id: UUID) -> Document:
        document = await self.documents.get(document_id)
        if document is None:
            raise LookupError(f"Document {document_id} was not found")
        if document.status is IngestionStatus.DELETED:
            return document
        if document.status.is_processing:
            raise DocumentInProcessingError(
                "Cannot delete while ingestion is in progress. Retry after the document "
                "reaches a terminal state.",
                details={"current_status": document.status.value},
            )
        if document.status is IngestionStatus.DELETING:
            return await self.cleanup.execute(document)
        if document.status not in _APPROVED_STATES:
            raise DocumentNotDeletableError(
                "The document can only be deleted after ingestion reaches a terminal state.",
                details={"current_status": document.status.value},
            )
        deleting = document.transition_to(IngestionStatus.DELETING)
        await self.documents.save(deleting)
        return await self.cleanup.execute(deleting)
