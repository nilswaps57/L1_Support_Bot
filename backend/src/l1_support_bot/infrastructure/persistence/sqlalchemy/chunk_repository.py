"""SQLAlchemy repository for prepared knowledge chunks and diagnostics."""

from collections.abc import Sequence
from datetime import UTC, datetime
from uuid import UUID, uuid4

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from l1_support_bot.domain.models.chunk import ChunkMetadata, KnowledgeChunk
from l1_support_bot.domain.models.parsed_document import ParseWarning
from l1_support_bot.infrastructure.persistence.models.chunks import (
    IngestionDiagnosticModel,
    KnowledgeChunkModel,
)
from l1_support_bot.infrastructure.persistence.models.ingestion_jobs import IngestionJobModel


class SqlAlchemyChunkRepository:
    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        self.session_factory = session_factory

    async def save_batch(self, chunks: Sequence[KnowledgeChunk]) -> None:
        models = [
            KnowledgeChunkModel(
                id=str(chunk.id),
                document_id=str(chunk.document_id),
                ingestion_job_id=str(chunk.ingestion_job_id),
                chunk_seq=chunk.sequence,
                text_preview=chunk.text[:500],
                text=chunk.text,
                source_type=chunk.metadata.source_type,
                page_number=chunk.metadata.page_number,
                section_path=chunk.metadata.section,
                task_code=chunk.metadata.task_code,
                screen_name=chunk.metadata.screen_name,
                module=chunk.metadata.module,
                functional_area=chunk.metadata.functional_area,
                menu_path=chunk.metadata.menu_path,
                prerequisites=list(chunk.metadata.prerequisites),
                modes=list(chunk.metadata.modes),
                field_names=list(chunk.metadata.field_names),
                procedure_steps=list(chunk.metadata.procedure_steps),
                error_code=chunk.metadata.error_code,
                jira_id=chunk.metadata.jira_id,
                rca_reference=chunk.metadata.rca_reference,
                element_type=chunk.metadata.element_type,
                embedding_model_id=chunk.embedding_model_id,
                index_generation_id=chunk.index_generation_id,
            )
            for chunk in chunks
        ]
        async with self.session_factory() as session:
            session.add_all(models)
            await session.commit()

    async def save_diagnostics(self, job_id: UUID, warnings: Sequence[ParseWarning | str]) -> None:
        models = [
            IngestionDiagnosticModel(
                id=str(uuid4()),
                ingestion_job_id=str(job_id),
                element_type=warning.element_type
                if isinstance(warning, ParseWarning)
                else "UNKNOWN",
                code=warning.code if isinstance(warning, ParseWarning) else None,
                description=warning.description if isinstance(warning, ParseWarning) else warning,
                page_number=warning.page_number if isinstance(warning, ParseWarning) else None,
                created_at=datetime.now(UTC),
            )
            for warning in warnings
        ]
        if not models:
            return
        async with self.session_factory() as session:
            session.add_all(models)
            await session.commit()

    async def delete_by_document(self, document_id: UUID) -> None:
        async with self.session_factory() as session:
            await session.execute(
                delete(KnowledgeChunkModel).where(
                    KnowledgeChunkModel.document_id == str(document_id)
                )
            )
            await session.commit()

    async def replace_for_document(
        self, document_id: UUID, chunks: Sequence[KnowledgeChunk]
    ) -> None:
        models = [
            KnowledgeChunkModel(
                id=str(chunk.id),
                document_id=str(chunk.document_id),
                ingestion_job_id=str(chunk.ingestion_job_id),
                chunk_seq=chunk.sequence,
                text_preview=chunk.text[:500],
                text=chunk.text,
                source_type=chunk.metadata.source_type,
                page_number=chunk.metadata.page_number,
                section_path=chunk.metadata.section,
                task_code=chunk.metadata.task_code,
                screen_name=chunk.metadata.screen_name,
                module=chunk.metadata.module,
                functional_area=chunk.metadata.functional_area,
                menu_path=chunk.metadata.menu_path,
                prerequisites=list(chunk.metadata.prerequisites),
                modes=list(chunk.metadata.modes),
                field_names=list(chunk.metadata.field_names),
                procedure_steps=list(chunk.metadata.procedure_steps),
                error_code=chunk.metadata.error_code,
                jira_id=chunk.metadata.jira_id,
                rca_reference=chunk.metadata.rca_reference,
                element_type=chunk.metadata.element_type,
                embedding_model_id=chunk.embedding_model_id,
                index_generation_id=chunk.index_generation_id,
            )
            for chunk in chunks
        ]
        async with self.session_factory() as session:
            await session.execute(
                delete(KnowledgeChunkModel).where(
                    KnowledgeChunkModel.document_id == str(document_id)
                )
            )
            session.add_all(models)
            await session.commit()

    async def delete_diagnostics_by_document(self, document_id: UUID) -> None:
        async with self.session_factory() as session:
            job_ids = select(IngestionJobModel.id).where(
                IngestionJobModel.document_id == str(document_id)
            )
            await session.execute(
                delete(IngestionDiagnosticModel).where(
                    IngestionDiagnosticModel.ingestion_job_id.in_(job_ids)
                )
            )
            await session.commit()


def to_domain(model: KnowledgeChunkModel) -> KnowledgeChunk:
    metadata = ChunkMetadata(
        document_name="Prepared document",
        source_type=model.source_type,
        page_number=model.page_number,
        section=model.section_path,
        task_code=model.task_code,
        screen_name=model.screen_name,
        module=model.module,
        functional_area=model.functional_area,
        menu_path=model.menu_path,
        prerequisites=tuple(model.prerequisites or []),
        modes=tuple(model.modes or []),
        field_names=tuple(model.field_names or []),
        procedure_steps=tuple(model.procedure_steps or []),
        error_code=model.error_code,
        jira_id=model.jira_id,
        rca_reference=model.rca_reference,
        element_type=model.element_type,
    )
    return KnowledgeChunk(
        id=UUID(model.id),
        document_id=UUID(model.document_id),
        ingestion_job_id=UUID(model.ingestion_job_id),
        sequence=model.chunk_seq,
        text=model.text,
        metadata=metadata,
        embedding_model_id=model.embedding_model_id,
        index_generation_id=model.index_generation_id,
    )
