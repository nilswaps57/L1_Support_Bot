"""Read-only document detail use case."""

from dataclasses import dataclass
from uuid import UUID

from l1_support_bot.domain.models.document import Document
from l1_support_bot.domain.models.ingestion import IngestionJob
from l1_support_bot.domain.ports.repositories import DocumentRepository, IngestionJobRepository


@dataclass(frozen=True, slots=True)
class DocumentDetails:
    document: Document
    latest_job: IngestionJob | None


class GetDocument:
    def __init__(
        self,
        *,
        document_repository: DocumentRepository,
        ingestion_job_repository: IngestionJobRepository,
    ) -> None:
        self.document_repository = document_repository
        self.ingestion_job_repository = ingestion_job_repository

    async def execute(self, document_id: UUID) -> DocumentDetails | None:
        document = await self.document_repository.get(document_id)
        if document is None:
            return None
        return DocumentDetails(
            document=document,
            latest_job=await self.ingestion_job_repository.latest_for_document(document.id),
        )