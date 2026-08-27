"""Asynchronous ingestion job queue contract."""

from typing import Protocol
from uuid import UUID

from l1_support_bot.domain.models.ingestion import IngestionJob


class JobQueuePort(Protocol):
    async def enqueue(self, job: IngestionJob) -> None: ...

    async def claim(self, *, worker_id: str) -> IngestionJob | None: ...

    async def acknowledge(self, job_id: UUID) -> None: ...

    async def release(self, job_id: UUID) -> None: ...
