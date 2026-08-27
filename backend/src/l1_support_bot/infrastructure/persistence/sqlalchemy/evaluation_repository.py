"""SQLAlchemy repository for reproducible RAG evaluation runs."""

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from l1_support_bot.domain.models.evaluation import EvaluationRun
from l1_support_bot.infrastructure.persistence.models.evaluation import EvaluationRunModel


class SqlAlchemyEvaluationRepository:
    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        self.session_factory = session_factory

    async def save(self, run: EvaluationRun) -> EvaluationRun:
        model = EvaluationRunModel(
            id=str(run.id),
            dataset_id=run.dataset_id,
            configuration_snapshot=dict(run.configuration_snapshot),
            retrieval_metrics=dict(run.retrieval_metrics),
            generation_metrics=dict(run.generation_metrics),
            started_at=run.started_at,
        )
        async with self.session_factory() as session:
            if await session.get(EvaluationRunModel, str(run.id)) is not None:
                raise ValueError(f"Evaluation run {run.id} already exists")
            session.add(model)
            await session.commit()
        return run
