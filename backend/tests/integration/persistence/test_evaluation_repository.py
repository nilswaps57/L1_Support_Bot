from datetime import UTC, datetime
from uuid import uuid4

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from l1_support_bot.domain.models.evaluation import EvaluationRun
from l1_support_bot.infrastructure.persistence.models import Base, EvaluationRunModel
from l1_support_bot.infrastructure.persistence.sqlalchemy.evaluation_repository import (
    SqlAlchemyEvaluationRepository,
)


@pytest.mark.integration
async def test_evaluation_repository_appends_runs_without_overwriting() -> None:
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)

    repository = SqlAlchemyEvaluationRepository(
        async_sessionmaker(engine, expire_on_commit=False)
    )
    first = EvaluationRun(
        dataset_id="dataset-v1",
        configuration_snapshot={"run_mode": "deterministic_fake"},
        retrieval_metrics={"recall_at_5": 1.0},
        generation_metrics={"groundedness_rate": 1.0},
        id=uuid4(),
        started_at=datetime(2026, 8, 27, tzinfo=UTC),
    )
    second = EvaluationRun(
        dataset_id="dataset-v1",
        configuration_snapshot={"run_mode": "live_ollama"},
        retrieval_metrics={"recall_at_5": 0.5},
        generation_metrics={"groundedness_rate": 0.5},
        id=uuid4(),
        started_at=datetime(2026, 8, 28, tzinfo=UTC),
    )

    assert await repository.save(first) == first
    assert await repository.save(second) == second

    async with async_sessionmaker(engine, expire_on_commit=False)() as session:
        rows = (await session.execute(select(EvaluationRunModel))).scalars().all()
    assert len(rows) == 2
    await engine.dispose()