"""Poll-based ingestion worker with safe retries and recovery."""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from uuid import uuid4

from l1_support_bot.domain.models.ingestion import IngestionJob, IngestionStatus
from l1_support_bot.domain.ports.job_queue import JobQueuePort
from l1_support_bot.domain.ports.repositories import DocumentRepository, IngestionJobRepository


class IngestionWorker:
    def __init__(
        self,
        *,
        queue: JobQueuePort,
        jobs: IngestionJobRepository,
        documents: DocumentRepository,
        process: Callable[[IngestionJob], Awaitable[IngestionJob]],
        worker_id: str | None = None,
    ) -> None:
        self.queue = queue
        self.jobs = jobs
        self.documents = documents
        self.process = process
        self.worker_id = worker_id or f"worker-{uuid4()}"

    async def run_once(self) -> IngestionJob | None:
        job = await self.queue.claim(worker_id=self.worker_id)
        if job is None:
            return None
        try:
            result = await self.process(job)
        except Exception as exc:
            current = await self.jobs.get(job.id) or job
            result = await self._failure(current, exc)
        await self.queue.acknowledge(job.id)
        return result

    async def run_forever(self, *, poll_seconds: float = 2.0) -> None:
        import asyncio

        while True:
            await self.run_once()
            await asyncio.sleep(poll_seconds)

    async def _failure(self, job: IngestionJob, error: Exception) -> IngestionJob:
        safe_message = self._safe_message(error)
        if job.attempt_count < job.max_attempts:
            status = IngestionStatus.QUEUED
        else:
            status = IngestionStatus.FAILED
        failed = IngestionJob(
            id=job.id,
            document_id=job.document_id,
            status=status,
            attempt_count=job.attempt_count,
            max_attempts=job.max_attempts,
            last_error=safe_message,
            last_error_category="PARSER_ERROR"
            if "parser" in safe_message.lower()
            else "PROCESSING_ERROR",
            parse_warnings=job.parse_warnings,
            created_at=job.created_at,
            started_at=None if status is IngestionStatus.QUEUED else job.started_at,
            completed_at=None,
            chunks_created=job.chunks_created,
            chunks_indexed=job.chunks_indexed,
            worker_id=None if status is IngestionStatus.QUEUED else job.worker_id,
            embedding_config_id=job.embedding_config_id,
        )
        saved = await self.jobs.update(failed)
        document = await self.documents.get(job.document_id)
        if document is not None:
            await self.documents.save(document.transition_to(status))
        return saved

    @staticmethod
    def _safe_message(error: Exception) -> str:
        message = str(error).strip()
        if not message or any(
            value in message.lower()
            for value in ("traceback", "/home/", "password", "token", "secret")
        ):
            return "The document could not be processed."
        return message[:500]


def run_worker() -> None:
    import asyncio

    from l1_support_bot.infrastructure.composition import build_default_worker
    from l1_support_bot.interface.config import get_settings

    engine, worker = build_default_worker(get_settings())
    try:
        asyncio.run(worker.run_forever())
    finally:
        asyncio.run(engine.dispose())


if __name__ == "__main__":
    run_worker()
