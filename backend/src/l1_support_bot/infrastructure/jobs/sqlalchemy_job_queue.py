"""Atomic persistent and in-memory job queues."""

from __future__ import annotations

import asyncio
from datetime import UTC, datetime, timedelta
from uuid import UUID

from sqlalchemy import or_, select, update
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from l1_support_bot.domain.models.ingestion import IngestionJob, IngestionStatus
from l1_support_bot.infrastructure.persistence.models.ingestion_jobs import IngestionJobModel
from l1_support_bot.infrastructure.persistence.sqlalchemy.ingestion_job_repository import _to_domain


class SqlAlchemyJobQueue:
    def __init__(
        self,
        session_factory: async_sessionmaker[AsyncSession],
        *,
        stale_after: timedelta = timedelta(minutes=15),
    ) -> None:
        self.session_factory = session_factory
        self.stale_after = stale_after

    async def enqueue(self, job: IngestionJob) -> None:
        async with self.session_factory() as session:
            await session.merge(
                IngestionJobModel(
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
            )
            await session.commit()

    async def claim(self, *, worker_id: str) -> IngestionJob | None:
        now = datetime.now(UTC)
        stale_before = now - self.stale_after
        async with self.session_factory() as session:
            await session.execute(
                update(IngestionJobModel)
                .where(
                    IngestionJobModel.status.in_(
                        [
                            IngestionStatus.PARSING.value,
                            IngestionStatus.NORMALISING.value,
                            IngestionStatus.CHUNKING.value,
                            IngestionStatus.EMBEDDING.value,
                            IngestionStatus.INDEXING.value,
                        ]
                    ),
                    IngestionJobModel.started_at.is_not(None),
                    IngestionJobModel.started_at < stale_before,
                )
                .values(status=IngestionStatus.QUEUED.value, worker_id=None, started_at=None)
            )
            candidate = await session.scalar(
                select(IngestionJobModel)
                .where(
                    IngestionJobModel.status == IngestionStatus.QUEUED.value,
                    or_(IngestionJobModel.worker_id.is_(None), IngestionJobModel.worker_id == ""),
                    IngestionJobModel.attempt_count < IngestionJobModel.max_attempts,
                )
                .order_by(IngestionJobModel.created_at)
                .limit(1)
            )
            if candidate is None:
                await session.commit()
                return None
            claimed = await session.execute(
                update(IngestionJobModel)
                .where(
                    IngestionJobModel.id == candidate.id,
                    IngestionJobModel.status == IngestionStatus.QUEUED.value,
                    or_(IngestionJobModel.worker_id.is_(None), IngestionJobModel.worker_id == ""),
                )
                .values(
                    worker_id=worker_id,
                    started_at=now,
                    attempt_count=IngestionJobModel.attempt_count + 1,
                )
            )
            if getattr(claimed, "rowcount", 0) != 1:
                await session.rollback()
                return None
            await session.commit()
            refreshed = await session.get(IngestionJobModel, candidate.id)
            return _to_domain(refreshed) if refreshed else None

    async def acknowledge(self, job_id: UUID) -> None:
        return None

    async def release(self, job_id: UUID) -> None:
        async with self.session_factory() as session:
            await session.execute(
                update(IngestionJobModel)
                .where(
                    IngestionJobModel.id == str(job_id),
                    IngestionJobModel.status == IngestionStatus.QUEUED.value,
                )
                .values(worker_id=None, started_at=None)
            )
            await session.commit()


class InMemoryJobQueue:
    def __init__(self, *, stale_after: timedelta = timedelta(minutes=15)) -> None:
        self.jobs: dict[UUID, IngestionJob] = {}
        self.stale_after = stale_after
        self._lock = asyncio.Lock()

    async def enqueue(self, job: IngestionJob) -> None:
        async with self._lock:
            self.jobs[job.id] = job

    async def claim(self, *, worker_id: str) -> IngestionJob | None:
        async with self._lock:
            now = datetime.now(UTC)
            for job_id, job in tuple(self.jobs.items()):
                if (
                    job.status
                    in {
                        IngestionStatus.PARSING,
                        IngestionStatus.NORMALISING,
                        IngestionStatus.CHUNKING,
                        IngestionStatus.EMBEDDING,
                        IngestionStatus.INDEXING,
                    }
                    and job.started_at
                    and now - job.started_at > self.stale_after
                ):
                    self.jobs[job_id] = IngestionJob(
                        id=job.id,
                        document_id=job.document_id,
                        status=IngestionStatus.QUEUED,
                        attempt_count=job.attempt_count,
                        max_attempts=job.max_attempts,
                        last_error=job.last_error,
                        last_error_category=job.last_error_category,
                        parse_warnings=job.parse_warnings,
                        created_at=job.created_at,
                        chunks_created=job.chunks_created,
                        chunks_indexed=job.chunks_indexed,
                        embedding_config_id=job.embedding_config_id,
                    )
            for job in sorted(self.jobs.values(), key=lambda item: item.created_at):
                if (
                    job.status is IngestionStatus.QUEUED
                    and job.worker_id is None
                    and job.attempt_count < job.max_attempts
                ):
                    claimed = IngestionJob(
                        id=job.id,
                        document_id=job.document_id,
                        status=job.status,
                        attempt_count=job.attempt_count + 1,
                        max_attempts=job.max_attempts,
                        last_error=job.last_error,
                        last_error_category=job.last_error_category,
                        parse_warnings=job.parse_warnings,
                        created_at=job.created_at,
                        started_at=now,
                        chunks_created=job.chunks_created,
                        chunks_indexed=job.chunks_indexed,
                        worker_id=worker_id,
                        embedding_config_id=job.embedding_config_id,
                    )
                    self.jobs[job.id] = claimed
                    return claimed
        return None

    async def acknowledge(self, job_id: UUID) -> None:
        return None

    async def release(self, job_id: UUID) -> None:
        async with self._lock:
            job = self.jobs.get(job_id)
            if job and job.status is IngestionStatus.QUEUED:
                self.jobs[job_id] = IngestionJob(
                    id=job.id,
                    document_id=job.document_id,
                    status=job.status,
                    attempt_count=job.attempt_count,
                    max_attempts=job.max_attempts,
                    last_error=job.last_error,
                    last_error_category=job.last_error_category,
                    parse_warnings=job.parse_warnings,
                    created_at=job.created_at,
                    chunks_created=job.chunks_created,
                    chunks_indexed=job.chunks_indexed,
                    embedding_config_id=job.embedding_config_id,
                )
