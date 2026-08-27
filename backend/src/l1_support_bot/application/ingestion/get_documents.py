"""Read-only document listing use case."""

from dataclasses import dataclass

from l1_support_bot.domain.models.document import Document, SourceType
from l1_support_bot.domain.models.ingestion import IngestionJob, IngestionStatus
from l1_support_bot.domain.ports.repositories import DocumentRepository, IngestionJobRepository


@dataclass(frozen=True, slots=True)
class DocumentSummary:
    document: Document
    latest_job: IngestionJob | None


@dataclass(frozen=True, slots=True)
class DocumentList:
    items: tuple[DocumentSummary, ...]
    total: int
    limit: int
    next_cursor: str | None


class GetDocuments:
    def __init__(
        self,
        *,
        document_repository: DocumentRepository,
        ingestion_job_repository: IngestionJobRepository,
    ) -> None:
        self.document_repository = document_repository
        self.ingestion_job_repository = ingestion_job_repository

    async def execute(
        self,
        *,
        limit: int = 20,
        cursor: str | None = None,
        status: IngestionStatus | None = None,
        source_type: SourceType | None = None,
    ) -> DocumentList:
        if not 1 <= limit <= 100:
            raise ValueError("Document list limit must be between 1 and 100")
        offset = self._parse_cursor(cursor)
        documents = tuple(
            await self.document_repository.list(status=status, source_type=source_type)
        )
        page = documents[offset : offset + limit]
        summaries_list: list[DocumentSummary] = []
        for document in page:
            latest_job = await self.ingestion_job_repository.latest_for_document(document.id)
            summaries_list.append(DocumentSummary(document=document, latest_job=latest_job))
        summaries = tuple(summaries_list)
        next_cursor = str(offset + limit) if offset + limit < len(documents) else None
        return DocumentList(summaries, len(documents), limit, next_cursor)

    @staticmethod
    def _parse_cursor(cursor: str | None) -> int:
        if cursor is None:
            return 0
        try:
            offset = int(cursor)
        except ValueError as exc:
            raise ValueError("Document list cursor must be a non-negative integer") from exc
        if offset < 0:
            raise ValueError("Document list cursor must be a non-negative integer")
        return offset