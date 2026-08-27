"""Prepare an uploaded document for the later embedding/indexing phase."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import replace
from uuid import UUID

from l1_support_bot.domain.errors import ProcessingError
from l1_support_bot.domain.models.configuration import ChunkingConfig, EmbeddingConfig
from l1_support_bot.domain.models.document import FileType
from l1_support_bot.domain.models.ingestion import IngestionJob, IngestionStatus
from l1_support_bot.domain.models.parsed_document import FlexcubeMetadata, ParseWarning
from l1_support_bot.domain.ports.chunking import ChunkerPort
from l1_support_bot.domain.ports.embedding import EmbeddingPort
from l1_support_bot.domain.ports.file_storage import FileStoragePort
from l1_support_bot.domain.ports.metadata import MetadataExtractorPort
from l1_support_bot.domain.ports.parsing import ParserPort
from l1_support_bot.domain.ports.repositories import (
    ChunkRepository,
    DocumentRepository,
    IngestionJobRepository,
)
from l1_support_bot.domain.ports.vector_store import VectorStorePort


class ProcessDocument:
    def __init__(
        self,
        *,
        document_repository: DocumentRepository,
        ingestion_job_repository: IngestionJobRepository,
        file_storage: FileStoragePort,
        parser: ParserPort,
        chunker: ChunkerPort,
        chunk_repository: ChunkRepository,
        metadata_extractor: MetadataExtractorPort | None = None,
        chunking_config: ChunkingConfig | None = None,
        pdf_fallback: ParserPort | None = None,
        docx_fallback: ParserPort | None = None,
        embedding: EmbeddingPort | None = None,
        vector_store: VectorStorePort | None = None,
        embedding_config: EmbeddingConfig | None = None,
    ) -> None:
        self.documents = document_repository
        self.jobs = ingestion_job_repository
        self.storage = file_storage
        self.parser = parser
        self.chunker = chunker
        self.chunks = chunk_repository
        self.config = chunking_config or ChunkingConfig()
        self.metadata_extractor = metadata_extractor
        self.pdf_fallback = pdf_fallback
        self.docx_fallback = docx_fallback
        self.embedding = embedding
        self.vector_store = vector_store
        self.embedding_config = embedding_config

    async def execute(self, job: IngestionJob) -> IngestionJob:
        document = await self.documents.get(job.document_id)
        if document is None:
            raise ValueError("The source document is no longer available.")
        content = await self.storage.read(document.storage_path)
        current = await self._transition(document.id, job, IngestionStatus.PARSING)
        warnings: list[ParseWarning] = []
        try:
            parsed = await self.parser.parse(content, document.file_type)
        except Exception:
            fallback = (
                self.pdf_fallback if document.file_type is FileType.PDF else self.docx_fallback
            )
            if fallback is None:
                raise ProcessingError("The document parser could not process this file.") from None
            parsed = await fallback.parse(content, document.file_type)
            warnings.append(
                ParseWarning(
                    "parser",
                    "The primary structured parser was unavailable; fallback parsing was used.",
                    code="PRIMARY_PARSER_FALLBACK",
                )
            )
        current = await self._transition(document.id, current, IngestionStatus.NORMALISING)
        metadata = (
            self.metadata_extractor.extract(parsed.elements)
            if self.metadata_extractor is not None
            else FlexcubeMetadata()
        )
        parsed = replace(
            parsed,
            document_name=document.name,
            source_type=document.source_type.value,
            metadata=metadata,
            warnings=parsed.warnings + tuple(warnings),
        )
        current = await self._transition(document.id, current, IngestionStatus.CHUNKING)
        prepared = await self.chunker.chunk(
            parsed, self.config, document_id=document.id, ingestion_job_id=job.id
        )
        if self.embedding_config is not None:
            prepared = tuple(
                replace(chunk, embedding_model_id=self.embedding_config.embedding_model_id)
                for chunk in prepared
            )
        await self.chunks.save_batch(prepared)
        diagnostics = parsed.all_warnings
        save_diagnostics = getattr(self.chunks, "save_diagnostics", None)
        if callable(save_diagnostics):
            await save_diagnostics(job.id, diagnostics)
        next_status = (
            IngestionStatus.READY_FOR_INDEXING_WITH_WARNING
            if diagnostics
            else IngestionStatus.READY_FOR_INDEXING
        )
        current = current.with_progress(
            status=next_status,
            chunks_created=len(prepared),
            parse_warnings=diagnostics,
        )
        current = await self._save(document.id, current)
        if self.embedding is None or self.vector_store is None or self.embedding_config is None:
            return current
        if not await self.vector_store.is_compatible(self.embedding_config.embedding_model_id):
            raise ProcessingError(
                "The active embedding model is incompatible with the existing index."
            )
        current = await self._transition(document.id, current, IngestionStatus.EMBEDDING)
        current = replace(current, embedding_config_id=self.embedding_config.config_id)
        current = await self._save(document.id, current)
        vectors: list[Sequence[float]] = []
        for start in range(0, len(prepared), self.embedding_config.batch_size):
            batch = prepared[start : start + self.embedding_config.batch_size]
            vectors.extend(
                await self.embedding.embed_batch(
                    [chunk.text for chunk in batch], self.embedding_config
                )
            )
        if len(vectors) != len(prepared) or any(
            len(vector) != self.embedding_config.dimensions for vector in vectors
        ):
            raise ProcessingError("Embedding generation returned incompatible vectors.")
        current = await self._transition(document.id, current, IngestionStatus.INDEXING)
        try:
            await self.vector_store.upsert(prepared, vectors)
        except Exception:
            try:
                await self.vector_store.delete_by_document(document.id)
                await self.chunks.delete_by_document(document.id)
            except Exception as cleanup_error:
                raise ProcessingError(
                    "Indexing failed and partial index cleanup could not be verified."
                ) from cleanup_error
            raise
        current = current.with_progress(
            status=(
                IngestionStatus.COMPLETED_WITH_WARNING
                if diagnostics
                else IngestionStatus.COMPLETED
            ),
            chunks_indexed=len(prepared),
        )
        return await self._save(document.id, current)

    async def _transition(
        self, document_id: UUID, job: IngestionJob, status: IngestionStatus
    ) -> IngestionJob:
        current = job.transition_to(status)
        await self.jobs.update(current)
        document = await self.documents.get(document_id)
        if document is not None:
            await self.documents.save(document.transition_to(status))
        return current

    async def _save(self, document_id: UUID, job: IngestionJob) -> IngestionJob:
        saved = await self.jobs.update(job)
        document = await self.documents.get(document_id)
        if document is not None:
            if document.status is not job.status:
                document = document.transition_to(job.status)
            await self.documents.save(document)
        return saved
