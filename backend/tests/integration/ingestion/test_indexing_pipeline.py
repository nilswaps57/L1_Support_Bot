
import pytest

from l1_support_bot.application.ingestion.process_document import ProcessDocument
from l1_support_bot.domain.models.configuration import EmbeddingConfig
from l1_support_bot.domain.models.document import Document, FileType, SourceType
from l1_support_bot.domain.models.ingestion import IngestionJob, IngestionStatus
from l1_support_bot.domain.models.parsed_document import DocumentElement, ParsedDocument
from l1_support_bot.infrastructure.chunking.structure_aware_chunker import StructureAwareChunker


class Documents:
    def __init__(self, document: Document) -> None:
        self.document = document

    async def get(self, document_id):
        return self.document

    async def save(self, document):
        self.document = document
        return document


class Jobs:
    def __init__(self, job: IngestionJob) -> None:
        self.job = job

    async def update(self, job):
        self.job = job
        return job


class Storage:
    async def read(self, path: str) -> bytes:
        return b"source"


class Parser:
    async def parse(self, content: bytes, file_type: FileType) -> ParsedDocument:
        return ParsedDocument(
            (DocumentElement("paragraph", "Task code BA435 opens the account screen."),),
            "md",
        )


class Chunks:
    async def save_batch(self, chunks):
        self.values = tuple(chunks)


class Embedding:
    async def embed_batch(self, texts, config):
        return tuple((1.0, 0.0, 0.0) for _ in texts)

    async def embed_query(self, text, config):
        return (1.0, 0.0, 0.0)


class Vector:
    def __init__(self) -> None:
        self.calls = 0

    async def upsert(self, chunks, vectors):
        self.calls += 1
        self.values = tuple(chunks)

    async def is_compatible(self, embedding_model_id):
        return True


@pytest.mark.asyncio
async def test_indexing_transitions_only_after_embedding_and_vector_upsert() -> None:
    document = Document.new(
        name="manual.md", original_filename="manual.md", file_type=FileType.MARKDOWN,
        source_type=SourceType.FLEXCUBE_MANUAL, checksum="b" * 64,
        storage_path="manual.md", file_size_bytes=6,
    ).transition_to(IngestionStatus.QUEUED)
    job = IngestionJob.new(document.id)
    documents, jobs, vector = Documents(document), Jobs(job), Vector()
    config = EmbeddingConfig(
        provider="fake", model="deterministic", model_version="1", endpoint="https://embed.test",
        dimensions=3, index_compat_id="fake:deterministic:1:3",
    )
    processor = ProcessDocument(
        document_repository=documents, ingestion_job_repository=jobs, file_storage=Storage(),
        parser=Parser(), chunker=StructureAwareChunker(), chunk_repository=Chunks(),
        embedding=Embedding(), vector_store=vector, embedding_config=config,
    )

    result = await processor.execute(job)

    assert result.status is IngestionStatus.COMPLETED
    assert result.chunks_indexed == 1
    assert vector.calls == 1
    assert documents.document.status.is_queryable
