"""Build and validate a replacement generation before making it active."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import replace
from uuid import UUID

from l1_support_bot.domain.errors import (
    CleanupFailedError,
    DocumentInProcessingError,
    DomainError,
    IncompatibleIndexError,
    ProcessingError,
)
from l1_support_bot.domain.models.configuration import ChunkingConfig, EmbeddingConfig
from l1_support_bot.domain.models.ingestion import IngestionJob, IngestionStatus
from l1_support_bot.domain.models.parsed_document import FlexcubeMetadata, ParseWarning
from l1_support_bot.domain.ports.chunking import ChunkerPort
from l1_support_bot.domain.ports.embedding import EmbeddingPort
from l1_support_bot.domain.ports.file_storage import FileStoragePort
from l1_support_bot.domain.ports.index_manager import IndexGeneration, IndexManagerPort
from l1_support_bot.domain.ports.metadata import MetadataExtractorPort
from l1_support_bot.domain.ports.parsing import ParserPort
from l1_support_bot.domain.ports.repositories import (
    ChunkRepository,
    DocumentRepository,
    IngestionJobRepository,
)

_ALLOWED_REINDEX_STATES = frozenset(
    {IngestionStatus.COMPLETED, IngestionStatus.COMPLETED_WITH_WARNING, IngestionStatus.FAILED}
)


def _chunking_config_id(config: ChunkingConfig) -> str:
    return ":".join(
        (
            config.strategy,
            str(config.target_chunk_tokens),
            str(config.min_chunk_tokens),
            str(config.max_chunk_tokens),
            str(config.overlap_tokens),
            str(config.table_as_unit),
            str(config.procedure_grouping),
        )
    )


class ReindexDocument:
    def __init__(
        self,
        *,
        documents: DocumentRepository,
        jobs: IngestionJobRepository,
        storage: FileStoragePort,
        parser: ParserPort,
        chunker: ChunkerPort,
        chunks: ChunkRepository,
        embedding: EmbeddingPort,
        embedding_config: EmbeddingConfig,
        index_manager: IndexManagerPort,
        metadata_extractor: MetadataExtractorPort | None = None,
        chunking_config: ChunkingConfig | None = None,
    ) -> None:
        self.documents = documents
        self.jobs = jobs
        self.storage = storage
        self.parser = parser
        self.chunker = chunker
        self.chunks = chunks
        self.embedding = embedding
        self.embedding_config = embedding_config
        self.index_manager = index_manager
        self.metadata_extractor = metadata_extractor
        self.chunking_config = chunking_config or ChunkingConfig()

    async def execute(self, document_id: UUID) -> IngestionJob:
        document = await self.documents.get(document_id)
        if document is None:
            raise LookupError(f"Document {document_id} was not found")
        if document.status.is_processing or document.status is IngestionStatus.DELETING:
            raise DocumentInProcessingError(
                "Cannot re-index while document processing is in progress.",
                details={"current_status": document.status.value},
            )
        if document.status not in _ALLOWED_REINDEX_STATES:
            raise ProcessingError(
                "The document must be in a terminal state before it can be re-indexed."
            )

        job = IngestionJob.new(document.id)
        await self.jobs.create(job)
        generation: IndexGeneration | None = None
        cutover_complete = False
        staging_cleanup_failure: CleanupFailedError | None = None
        staging_cleanup_error: Exception | None = None
        try:
            job = await self._transition(job, IngestionStatus.PARSING)
            parsed = await self.parser.parse(
                await self.storage.read(document.storage_path), document.file_type
            )
            warnings: Sequence[ParseWarning] = parsed.all_warnings
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
            )
            job = await self._transition(job, IngestionStatus.NORMALISING)
            job = await self._transition(job, IngestionStatus.CHUNKING)
            prepared = await self.chunker.chunk(
                parsed,
                self.chunking_config,
                document_id=document.id,
                ingestion_job_id=job.id,
            )
            prepared = tuple(
                replace(chunk, embedding_model_id=self.embedding_config.embedding_model_id)
                for chunk in prepared
            )
            job = await self._transition(
                job,
                IngestionStatus.READY_FOR_INDEXING_WITH_WARNING
                if warnings
                else IngestionStatus.READY_FOR_INDEXING,
            )
            generation = await self.index_manager.begin_staging(
                document.id,
                embedding_model_id=self.embedding_config.embedding_model_id,
                chunking_config_id=_chunking_config_id(self.chunking_config),
            )
            prepared = tuple(
                replace(chunk, index_generation_id=generation.generation_id)
                for chunk in prepared
            )
            job = await self._transition(job, IngestionStatus.EMBEDDING)
            vectors: list[tuple[float, ...]] = []
            for start in range(0, len(prepared), self.embedding_config.batch_size):
                batch = prepared[start : start + self.embedding_config.batch_size]
                vectors.extend(
                    tuple(vector)
                    for vector in await self.embedding.embed_batch(
                        [chunk.text for chunk in batch], self.embedding_config
                    )
                )
            if len(vectors) != len(prepared) or any(
                len(vector) != self.embedding_config.dimensions for vector in vectors
            ):
                raise IncompatibleIndexError(
                    "Replacement embeddings are incompatible with the index."
                )
            job = await self._transition(job, IngestionStatus.INDEXING)
            await self.index_manager.stage(generation, prepared, tuple(vectors))
            await self.index_manager.validate(
                generation,
                document_id=document.id,
                expected_chunks=len(prepared),
                embedding_model_id=self.embedding_config.embedding_model_id,
            )
            previous = await self.index_manager.cutover(generation)
            cutover_complete = True
            try:
                await self.chunks.replace_for_document(document.id, prepared)
            except Exception:
                if previous is not None:
                    await self.index_manager.rollback(previous)
                await self.index_manager.cleanup(generation)
                raise
            if previous is not None:
                await self.index_manager.cleanup(previous)
            result_status = (
                IngestionStatus.COMPLETED_WITH_WARNING if warnings else IngestionStatus.COMPLETED
            )
            job = job.with_progress(
                status=result_status,
                chunks_created=len(prepared),
                chunks_indexed=len(prepared),
                parse_warnings=tuple(warnings),
                chunking_config_snapshot=generation.chunking_config_id,
            )
            saved = await self.jobs.update(job)
            await self.documents.save(document.transition_to(result_status))
            return saved
        except Exception as exc:
            if generation is not None and not cutover_complete:
                try:
                    await self.index_manager.cleanup(generation)
                except Exception as cleanup_error:
                    staging_cleanup_failure = CleanupFailedError(
                        "The failed replacement index could not be removed safely."
                    )
                    staging_cleanup_error = cleanup_error
            failure = staging_cleanup_failure or exc
            failed = job.with_progress(
                status=IngestionStatus.FAILED,
                last_error=(
                    failure.safe_message
                    if isinstance(failure, DomainError)
                    else "Re-indexing failed."
                ),
            )
            await self.jobs.update(failed)
            if staging_cleanup_failure is not None:
                raise staging_cleanup_failure from staging_cleanup_error
            raise

    async def _transition(self, job: IngestionJob, status: IngestionStatus) -> IngestionJob:
        updated = job.transition_to(status)
        return await self.jobs.update(updated)
