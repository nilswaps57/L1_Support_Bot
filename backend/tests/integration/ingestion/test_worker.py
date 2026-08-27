from dataclasses import replace
from datetime import UTC, datetime, timedelta
from uuid import uuid4

import pytest

from l1_support_bot.domain.models.ingestion import IngestionJob, IngestionStatus
from l1_support_bot.infrastructure.jobs.sqlalchemy_job_queue import InMemoryJobQueue


@pytest.mark.asyncio
async def test_queue_claim_is_atomic_and_only_one_worker_gets_job() -> None:
    queue = InMemoryJobQueue()
    job = IngestionJob.new(uuid4())
    await queue.enqueue(job)

    first, second = await __import__("asyncio").gather(
        queue.claim(worker_id="worker-a"), queue.claim(worker_id="worker-b")
    )

    assert (first is None) != (second is None)
    assert (first or second).worker_id in {"worker-a", "worker-b"}


@pytest.mark.asyncio
async def test_stale_claim_is_recovered() -> None:
    queue = InMemoryJobQueue(stale_after=timedelta(seconds=1))
    job = IngestionJob.new(uuid4()).transition_to(IngestionStatus.PARSING)
    stale = replace(job, started_at=datetime.now(UTC) - timedelta(seconds=5))
    await queue.enqueue(stale)

    recovered = await queue.claim(worker_id="recovery")

    assert recovered is not None
    assert recovered.worker_id == "recovery"
