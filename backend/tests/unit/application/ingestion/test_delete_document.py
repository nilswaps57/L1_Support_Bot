from dataclasses import dataclass, field
from uuid import UUID

import pytest

from l1_support_bot.application.ingestion.cleanup_document import CleanupDocument
from l1_support_bot.application.ingestion.delete_document import DeleteDocument
from l1_support_bot.domain.errors import CleanupFailedError, DocumentInProcessingError
from l1_support_bot.domain.models.document import Document, FileType, SourceType
from l1_support_bot.domain.models.ingestion import IngestionJob, IngestionStatus


def make_document(status: IngestionStatus) -> Document:
    document = Document.new(
        name="manual.md",
        original_filename="manual.md",
        file_type=FileType.MARKDOWN,
        source_type=SourceType.FLEXCUBE_MANUAL,
        checksum="a" * 64,
        storage_path="manual.md",
        file_size_bytes=4,
    )
    document = document.transition_to(IngestionStatus.QUEUED)
    if status is IngestionStatus.QUEUED:
        return document
    if status is IngestionStatus.FAILED:
        return document.transition_to(status)
    stages = (
        IngestionStatus.PARSING,
        IngestionStatus.NORMALISING,
        IngestionStatus.CHUNKING,
    )
    for transition in stages:
        document = document.transition_to(transition)
        if transition is status:
            return document
    if status is IngestionStatus.READY_FOR_INDEXING_WITH_WARNING:
        return document.transition_to(status)
    for transition in (
        IngestionStatus.READY_FOR_INDEXING,
        IngestionStatus.EMBEDDING,
        IngestionStatus.INDEXING,
    ):
        document = document.transition_to(transition)
        if transition is status:
            return document
    document = document.transition_to(status)
    return document


@dataclass
class Documents:
    document: Document

    async def get(self, document_id: UUID):
        return self.document if self.document.id == document_id else None

    async def save(self, document: Document):
        self.document = document
        return document


@dataclass
class Jobs:
    jobs: list[IngestionJob] = field(default_factory=list)

    async def delete_by_document(self, document_id: UUID) -> None:
        self.jobs = [job for job in self.jobs if job.document_id != document_id]


@dataclass
class Chunks:
    deleted: list[UUID] = field(default_factory=list)

    async def delete_by_document(self, document_id: UUID) -> None:
        self.deleted.append(document_id)


@dataclass
class Diagnostics:
    deleted: list[UUID] = field(default_factory=list)

    async def delete_diagnostics_by_document(self, document_id: UUID) -> None:
        self.deleted.append(document_id)


@dataclass
class Vectors:
    deleted: list[UUID] = field(default_factory=list)

    async def delete_by_document(self, document_id: UUID) -> None:
        self.deleted.append(document_id)


@dataclass
class Storage:
    deleted: list[str] = field(default_factory=list)

    async def delete(self, storage_path: str) -> None:
        self.deleted.append(storage_path)


async def delete_use_case(document: Document, *, storage=None, vectors=None):
    documents = Documents(document)
    chunks = Chunks()
    jobs = Jobs([IngestionJob.new(document.id)])
    diagnostics = Diagnostics()
    storage = storage or Storage()
    vectors = vectors or Vectors()
    cleanup = CleanupDocument(
        documents=documents,
        jobs=jobs,
        chunks=chunks,
        diagnostics=diagnostics,
        vectors=vectors,
        storage=storage,
    )
    return await DeleteDocument(documents=documents, cleanup=cleanup).execute(document.id)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "status",
    [
        IngestionStatus.COMPLETED,
        IngestionStatus.COMPLETED_WITH_WARNING,
        IngestionStatus.FAILED,
    ],
)
async def test_terminal_documents_are_deleted_and_cleanup_is_repeatable(status) -> None:
    document = make_document(status)
    result = await delete_use_case(document)

    assert result.status is IngestionStatus.DELETED


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "status",
    [
        IngestionStatus.QUEUED,
        IngestionStatus.PARSING,
        IngestionStatus.NORMALISING,
        IngestionStatus.CHUNKING,
        IngestionStatus.READY_FOR_INDEXING,
        IngestionStatus.READY_FOR_INDEXING_WITH_WARNING,
        IngestionStatus.EMBEDDING,
        IngestionStatus.INDEXING,
    ],
)
async def test_active_ingestion_is_rejected_without_changing_the_document(status) -> None:
    document = make_document(status)
    with pytest.raises(DocumentInProcessingError) as error:
        await delete_use_case(document)

    assert error.value.code == "DOCUMENT_IN_PROCESSING"
    assert error.value.details["current_status"] == status.value


@pytest.mark.asyncio
async def test_cleanup_failure_never_reports_deleted_and_can_be_retried() -> None:
    document = make_document(IngestionStatus.COMPLETED)
    failing_vectors = Vectors()
    original_delete = failing_vectors.delete_by_document
    calls = 0

    async def fail_once(document_id: UUID) -> None:
        nonlocal calls
        calls += 1
        if calls == 1:
            raise OSError("vector store unavailable")
        await original_delete(document_id)

    failing_vectors.delete_by_document = fail_once  # type: ignore[method-assign]
    documents = Documents(document)
    cleanup = CleanupDocument(
        documents=documents,
        jobs=Jobs(),
        chunks=Chunks(),
        diagnostics=Diagnostics(),
        vectors=failing_vectors,
        storage=Storage(),
    )
    use_case = DeleteDocument(documents=documents, cleanup=cleanup)

    with pytest.raises(CleanupFailedError):
        await use_case.execute(document.id)
    assert documents.document.status is IngestionStatus.DELETING

    result = await use_case.execute(document.id)
    assert result.status is IngestionStatus.DELETED
    assert calls == 2
