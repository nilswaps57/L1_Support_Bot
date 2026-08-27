from dataclasses import dataclass
from uuid import UUID

import pytest

from l1_support_bot.application.ingestion.process_document import ProcessDocument
from l1_support_bot.domain.models.document import Document, FileType, SourceType
from l1_support_bot.domain.models.ingestion import IngestionJob, IngestionStatus
from l1_support_bot.domain.models.parsed_document import (
    DocumentElement,
    ParsedDocument,
    ParseWarning,
)
from l1_support_bot.infrastructure.chunking.structure_aware_chunker import StructureAwareChunker
from l1_support_bot.infrastructure.parsing.flexcube_metadata_extractor import (
    FlexcubeMetadataExtractor,
)


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
    job: IngestionJob

    async def update(self, job: IngestionJob):
        self.job = job
        return job


class Storage:
    async def read(self, storage_path: str) -> bytes:
        return b"source"


class Parser:
    async def parse(self, content: bytes, file_type: FileType) -> ParsedDocument:
        raise ValueError("parser failed")


class Fallback:
    async def parse(self, content: bytes, file_type: FileType) -> ParsedDocument:
        return ParsedDocument(
            (DocumentElement("table", "Field | Value", page_number=4),),
            "pdf",
            warnings=(ParseWarning("table", "A table could not be fully parsed", page_number=4),),
        )


class Chunks:
    def __init__(self) -> None:
        self.values = ()
        self.diagnostics = ()

    async def save_batch(self, chunks):
        self.values = tuple(chunks)

    async def save_diagnostics(self, job_id, warnings):
        self.diagnostics = tuple(warnings)


@pytest.mark.asyncio
async def test_processing_stops_before_embeddings_and_preserves_warning() -> None:
    document = Document.new(
        name="manual.pdf",
        original_filename="manual.pdf",
        file_type=FileType.PDF,
        source_type=SourceType.FLEXCUBE_MANUAL,
        checksum="a" * 64,
        storage_path="manual.pdf",
        file_size_bytes=6,
    ).transition_to(IngestionStatus.QUEUED)
    job = IngestionJob.new(document.id)
    documents = Documents(document)
    jobs = Jobs(job)
    chunks = Chunks()
    processor = ProcessDocument(
        document_repository=documents,
        ingestion_job_repository=jobs,
        file_storage=Storage(),
        parser=Parser(),
        pdf_fallback=Fallback(),
        docx_fallback=Fallback(),
        metadata_extractor=FlexcubeMetadataExtractor(),
        chunker=StructureAwareChunker(),
        chunk_repository=chunks,
    )

    result = await processor.execute(job)

    assert result.status is IngestionStatus.READY_FOR_INDEXING_WITH_WARNING
    assert not result.status.is_queryable
    assert result.chunks_created == 1
    assert chunks.diagnostics[0].page_number == 4
    assert documents.document.status is IngestionStatus.READY_FOR_INDEXING_WITH_WARNING
