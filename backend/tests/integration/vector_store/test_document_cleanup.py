from dataclasses import dataclass, field
from uuid import UUID, uuid4

import pytest

from l1_support_bot.application.ingestion.cleanup_document import CleanupDocument
from l1_support_bot.domain.models.document import Document, FileType, SourceType
from l1_support_bot.domain.models.ingestion import IngestionStatus


def document() -> Document:
    item = Document.new(
        name="manual.md",
        original_filename="manual.md",
        file_type=FileType.MARKDOWN,
        source_type=SourceType.FLEXCUBE_MANUAL,
        checksum="b" * 64,
        storage_path="manual.md",
        file_size_bytes=4,
    )
    for transition in (
        IngestionStatus.QUEUED,
        IngestionStatus.PARSING,
        IngestionStatus.NORMALISING,
        IngestionStatus.CHUNKING,
        IngestionStatus.READY_FOR_INDEXING,
        IngestionStatus.EMBEDDING,
        IngestionStatus.INDEXING,
        IngestionStatus.COMPLETED,
    ):
        item = item.transition_to(transition)
    return item


@dataclass
class Vectors:
    chunks: dict[UUID, UUID] = field(default_factory=dict)

    async def delete_by_document(self, document_id: UUID) -> None:
        self.chunks = {
            chunk_id: owner for chunk_id, owner in self.chunks.items() if owner != document_id
        }


@dataclass
class Chunks:
    chunks: dict[UUID, UUID]

    async def delete_by_document(self, document_id: UUID) -> None:
        self.chunks = {
            chunk_id: owner for chunk_id, owner in self.chunks.items() if owner != document_id
        }


@dataclass
class Jobs:
    document_id: UUID
    deleted: bool = False

    async def delete_by_document(self, document_id: UUID) -> None:
        self.deleted = document_id == self.document_id


@dataclass
class Diagnostics:
    deleted: bool = False

    async def delete_diagnostics_by_document(self, document_id: UUID) -> None:
        self.deleted = True


@dataclass
class Documents:
    value: Document

    async def save(self, value: Document) -> Document:
        self.value = value
        return value


@dataclass
class Storage:
    files: set[str]

    async def delete(self, path: str) -> None:
        self.files.discard(path)


@pytest.mark.integration
@pytest.mark.asyncio
async def test_cleanup_removes_vectors_chunks_diagnostics_jobs_and_source() -> None:
    item = document()
    vectors = Vectors({uuid4(): item.id})
    chunks = Chunks({uuid4(): item.id, uuid4(): uuid4()})
    jobs = Jobs(item.id)
    diagnostics = Diagnostics()
    storage = Storage({item.storage_path})
    documents = Documents(item)

    result = await CleanupDocument(
        documents=documents,
        jobs=jobs,
        chunks=chunks,
        diagnostics=diagnostics,
        vectors=vectors,
        storage=storage,
    ).execute(item.transition_to(IngestionStatus.DELETING))

    assert result.status is IngestionStatus.DELETED
    assert not vectors.chunks
    assert len(chunks.chunks) == 1
    assert jobs.deleted
    assert diagnostics.deleted
    assert not storage.files


@pytest.mark.integration
@pytest.mark.asyncio
async def test_cleanup_is_idempotent_for_missing_records() -> None:
    item = document().transition_to(IngestionStatus.DELETING)
    result = await CleanupDocument(
        documents=Documents(item),
        jobs=Jobs(item.id),
        chunks=Chunks({}),
        diagnostics=Diagnostics(),
        vectors=Vectors(),
        storage=Storage(set()),
    ).execute(item)

    assert result.status is IngestionStatus.DELETED
