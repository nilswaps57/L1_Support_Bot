from datetime import UTC, datetime, timedelta
from uuid import uuid4

import pytest
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from l1_support_bot.domain.models.ingestion import IngestionJob, IngestionStatus
from l1_support_bot.infrastructure.jobs.sqlalchemy_job_queue import SqlAlchemyJobQueue
from l1_support_bot.infrastructure.persistence.models import Base
from l1_support_bot.infrastructure.persistence.models.ingestion_jobs import IngestionJobModel


@pytest.mark.asyncio
async def test_sql_queue_claim_is_exclusive_and_recovers_stale_worker() -> None:
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    sessions = async_sessionmaker(engine, expire_on_commit=False)
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)

    queue = SqlAlchemyJobQueue(sessions, stale_after=timedelta(seconds=1))
    queued = IngestionJob.new(uuid4())
    await queue.enqueue(queued)
    first, second = await __import__("asyncio").gather(
        queue.claim(worker_id="worker-a"), queue.claim(worker_id="worker-b")
    )
    assert (first is None) != (second is None)

    stale = IngestionJob(
        id=uuid4(),
        document_id=uuid4(),
        status=IngestionStatus.PARSING,
        attempt_count=1,
        started_at=datetime.now(UTC) - timedelta(seconds=5),
    )
    async with sessions() as session:
        session.add(
            IngestionJobModel(
                id=str(stale.id), document_id=str(stale.document_id), status=stale.status.value,
                attempt_count=stale.attempt_count, max_attempts=stale.max_attempts,
                parse_warnings=[], created_at=stale.created_at, started_at=stale.started_at,
                chunks_created=0, chunks_indexed=0,
            )
        )
        await session.commit()

    recovered = await queue.claim(worker_id="recovery")
    assert recovered is not None
    assert recovered.id == stale.id
    assert recovered.worker_id == "recovery"
    await engine.dispose()
