"""SQLAlchemy ingestion-job repository."""

from collections.abc import Sequence
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from l1_support_bot.domain.models.ingestion import IngestionJob, IngestionStatus
from l1_support_bot.domain.models.parsed_document import ParseWarning
from l1_support_bot.infrastructure.persistence.models.ingestion_jobs import IngestionJobModel


def _to_domain(model: IngestionJobModel) -> IngestionJob:
    return IngestionJob(
        id=UUID(model.id),
        document_id=UUID(model.document_id),
        status=IngestionStatus(model.status),
        attempt_count=model.attempt_count,
        max_attempts=model.max_attempts,
        last_error=model.last_error,
        last_error_category=model.last_error_category,
        parse_warnings=tuple(
            ParseWarning(**warning) if isinstance(warning, dict) else warning
            for warning in (model.parse_warnings or [])
        ),
        created_at=model.created_at,
        started_at=model.started_at,
        completed_at=model.completed_at,
        chunks_created=model.chunks_created,
        chunks_indexed=model.chunks_indexed,
        worker_id=model.worker_id,
        embedding_config_id=model.embedding_config_id,
    )


class SqlAlchemyIngestionJobRepository:
    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        self.session_factory = session_factory

    async def create(self, job: IngestionJob) -> IngestionJob:
        return await self._save(job, create_only=True)

    async def get(self, job_id: UUID) -> IngestionJob | None:
        async with self.session_factory() as session:
            model = await session.get(IngestionJobModel, str(job_id))
            return _to_domain(model) if model else None

    async def update(self, job: IngestionJob) -> IngestionJob:
        return await self._save(job, create_only=False)

    async def list_pending(self, *, limit: int = 10) -> Sequence[IngestionJob]:
        async with self.session_factory() as session:
            statement = (
                select(IngestionJobModel)
                .where(IngestionJobModel.status == IngestionStatus.QUEUED.value)
                .order_by(IngestionJobModel.created_at)
                .limit(limit)
            )
            result = await session.scalars(statement)
            return tuple(_to_domain(model) for model in result)

    async def latest_for_document(self, document_id: UUID) -> IngestionJob | None:
        async with self.session_factory() as session:
            statement = (
                select(IngestionJobModel)
                .where(IngestionJobModel.document_id == str(document_id))
                .order_by(IngestionJobModel.created_at.desc())
                .limit(1)
            )
            model = await session.scalar(statement)
            return _to_domain(model) if model else None

    async def _save(self, job: IngestionJob, *, create_only: bool) -> IngestionJob:
        model = IngestionJobModel(
            id=str(job.id),
            document_id=str(job.document_id),
            status=job.status.value,
            attempt_count=job.attempt_count,
            max_attempts=job.max_attempts,
            last_error=job.last_error,
            last_error_category=job.last_error_category,
            parse_warnings=[
                warning
                if isinstance(warning, str)
                else {
                    "element_type": warning.element_type,
                    "description": warning.description,
                    "page_number": warning.page_number,
                    "code": warning.code,
                }
                for warning in job.parse_warnings
            ],
            created_at=job.created_at,
            started_at=job.started_at,
            completed_at=job.completed_at,
            chunks_created=job.chunks_created,
            chunks_indexed=job.chunks_indexed,
            worker_id=job.worker_id,
            embedding_config_id=job.embedding_config_id,
        )
        async with self.session_factory() as session:
            if create_only:
                session.add(model)
            else:
                await session.merge(model)
            await session.commit()
        return job