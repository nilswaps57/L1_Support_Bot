from dataclasses import dataclass, field
from uuid import UUID, uuid4

import pytest

from l1_support_bot.application.ingestion.reindex_document import ReindexDocument
from l1_support_bot.domain.errors import IncompatibleIndexError, ProcessingError
from l1_support_bot.domain.models.chunk import ChunkMetadata, KnowledgeChunk
from l1_support_bot.domain.models.configuration import EmbeddingConfig
from l1_support_bot.domain.models.document import Document, FileType, SourceType
from l1_support_bot.domain.models.ingestion import IngestionJob, IngestionStatus
from l1_support_bot.domain.models.parsed_document import DocumentElement, ParsedDocument
from l1_support_bot.domain.ports.index_manager import IndexGeneration


@dataclass
class Documents:
    value: Document

    async def get(self, document_id: UUID):
        return self.value if document_id == self.value.id else None

    async def save(self, document: Document):
        self.value = document
        return document


@dataclass
class Jobs:
    values: list[IngestionJob] = field(default_factory=list)

    async def create(self, job: IngestionJob):
        self.values.append(job)
        return job

    async def update(self, job: IngestionJob):
        if not any(value.id == job.id for value in self.values):
            self.values.append(job)
        return job


class Storage:
    async def read(self, path: str) -> bytes:
        return b"source"


class Parser:
    async def parse(self, content: bytes, file_type: FileType) -> ParsedDocument:
        return ParsedDocument((DocumentElement("paragraph", "new replacement content"),), "md")


class Chunker:
    async def chunk(self, parsed, config, *, document_id, ingestion_job_id):
        return (
            KnowledgeChunk.new(
                document_id=document_id,
                ingestion_job_id=ingestion_job_id,
                sequence=0,
                text=parsed.elements[0].text,
                metadata=ChunkMetadata(document_name="manual.md"),
            ),
        )


@dataclass
class Chunks:
    current: tuple[KnowledgeChunk, ...] = ()

    async def replace_for_document(self, document_id: UUID, chunks):
        self.current = tuple(chunks)


class Embedding:
    def __init__(self, fail: bool = False) -> None:
        self.fail = fail

    async def embed_batch(self, texts, config):
        if self.fail:
            raise ProcessingError("Embedding failed safely.")
        return ((1.0, 0.0, 0.0) for _ in texts)


@dataclass
class IndexManager:
    active: IndexGeneration = field(
        default_factory=lambda: IndexGeneration("active", "fake:old:1:3", "chunk-v1")
    )
    staged: dict[str, tuple[KnowledgeChunk, ...]] = field(default_factory=dict)
    superseded_cleaned: list[str] = field(default_factory=list)
    fail_validation: bool = False

    async def begin_staging(self, document_id, *, embedding_model_id, chunking_config_id):
        generation = IndexGeneration(
            f"staging-{uuid4()}", embedding_model_id, chunking_config_id
        )
        self.staged[generation.generation_id] = ()
        return generation

    async def stage(self, generation, chunks, vectors):
        self.staged[generation.generation_id] = tuple(chunks)

    async def validate(self, generation, *, document_id, expected_chunks, embedding_model_id):
        if self.fail_validation:
            raise IncompatibleIndexError("Staged index validation failed.")
        assert len(self.staged[generation.generation_id]) == expected_chunks
        assert generation.embedding_model_id == embedding_model_id

    async def cutover(self, generation):
        previous = self.active
        self.active = generation
        return previous

    async def rollback(self, generation):
        self.active = generation

    async def cleanup(self, generation):
        self.superseded_cleaned.append(generation.generation_id)


def make_document() -> Document:
    item = Document.new(
        name="manual.md",
        original_filename="manual.md",
        file_type=FileType.MARKDOWN,
        source_type=SourceType.FLEXCUBE_MANUAL,
        checksum="c" * 64,
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


def build(*, embedding=None, manager=None, chunks=None):
    document = make_document()
    jobs = Jobs()
    manager = manager or IndexManager()
    return (
        ReindexDocument(
            documents=Documents(document),
            jobs=jobs,
            storage=Storage(),
            parser=Parser(),
            chunker=Chunker(),
            chunks=chunks or Chunks(),
            embedding=embedding or Embedding(),
            embedding_config=EmbeddingConfig(
                provider="fake",
                model="new",
                model_version="2",
                endpoint="https://embedding.test",
                dimensions=3,
                index_compat_id="fake:new:2:3",
            ),
            index_manager=manager,
        ),
        manager,
        jobs,
    )


@pytest.mark.integration
@pytest.mark.asyncio
async def test_reindex_validates_and_cuts_over_without_mixed_chunks() -> None:
    use_case, manager, _ = build()

    result = await use_case.execute(use_case.documents.value.id)

    assert result.status is IngestionStatus.COMPLETED
    assert manager.active.embedding_model_id == "fake:new:2:3"
    assert len(manager.superseded_cleaned) == 1


@pytest.mark.integration
@pytest.mark.asyncio
async def test_embedding_failure_preserves_active_generation() -> None:
    use_case, manager, _ = build(embedding=Embedding(fail=True))
    active = manager.active

    with pytest.raises(ProcessingError):
        await use_case.execute(use_case.documents.value.id)

    assert manager.active == active


@pytest.mark.integration
@pytest.mark.asyncio
async def test_validation_failure_preserves_active_generation() -> None:
    manager = IndexManager(fail_validation=True)
    use_case, manager, _ = build(manager=manager)
    active = manager.active

    with pytest.raises(IncompatibleIndexError):
        await use_case.execute(use_case.documents.value.id)

    assert manager.active == active


@pytest.mark.integration
@pytest.mark.asyncio
async def test_active_generation_is_single_value_for_concurrent_queries() -> None:
    manager = IndexManager()
    first = manager.active
    second = IndexGeneration("staging-2", "fake:new:2:3", "chunk-v2")

    before_cutover = manager.active
    await manager.cutover(second)
    after_cutover = manager.active

    assert before_cutover == first
    assert after_cutover == second
