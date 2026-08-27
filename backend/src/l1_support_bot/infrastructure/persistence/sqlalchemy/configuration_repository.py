"""SQLAlchemy repository for embedding configuration."""

from datetime import UTC, datetime
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from l1_support_bot.domain.models.configuration import EmbeddingConfig
from l1_support_bot.infrastructure.persistence.models.configuration import (
    EmbeddingConfigurationModel,
)


class SqlAlchemyConfigurationRepository:
    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        self.session_factory = session_factory

    async def get_embedding(self) -> EmbeddingConfig | None:
        async with self.session_factory() as session:
            model = await session.scalar(
                select(EmbeddingConfigurationModel)
                .where(EmbeddingConfigurationModel.is_active.is_(True))
                .order_by(EmbeddingConfigurationModel.updated_at.desc())
                .limit(1)
            )
            return self._to_domain(model) if model else None

    async def save_embedding(self, config: EmbeddingConfig) -> EmbeddingConfig:
        now = datetime.now(UTC)
        model = EmbeddingConfigurationModel(
            id=str(uuid4()),
            provider=config.provider,
            model=config.model,
            model_version=config.model_version,
            endpoint=config.endpoint,
            dimensions=config.dimensions,
            distance_method=config.distance_method,
            index_compat_id=config.index_compat_id,
            batch_size=config.batch_size,
            timeout_seconds=config.timeout_seconds,
            is_active=config.is_active,
            label=config.label,
            created_at=now,
            updated_at=now,
        )
        async with self.session_factory() as session:
            if config.is_active:
                active = await session.scalars(
                    select(EmbeddingConfigurationModel).where(
                        EmbeddingConfigurationModel.is_active.is_(True)
                    )
                )
                for item in active:
                    item.is_active = False
            session.add(model)
            await session.commit()
        return config

    @staticmethod
    def _to_domain(model: EmbeddingConfigurationModel) -> EmbeddingConfig:
        return EmbeddingConfig(
            provider=model.provider,
            model=model.model,
            model_version=model.model_version,
            endpoint=model.endpoint,
            dimensions=model.dimensions,
            distance_method=model.distance_method,
            index_compat_id=model.index_compat_id,
            batch_size=model.batch_size,
            timeout_seconds=model.timeout_seconds,
            is_active=model.is_active,
            label=model.label,
            config_id=model.id,
        )
