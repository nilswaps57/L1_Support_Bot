import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from l1_support_bot.domain.models.configuration import (
    ChunkingConfig,
    ConfigurationSnapshot,
    EmbeddingConfig,
    LLMConfig,
    RetrievalConfig,
)
from l1_support_bot.infrastructure.persistence.models import Base
from l1_support_bot.infrastructure.persistence.models.configuration import (
    EmbeddingConfigurationModel,
)
from l1_support_bot.infrastructure.persistence.models.llm_config import (
    ChunkingConfigurationModel,
    LLMConfigurationModel,
)
from l1_support_bot.infrastructure.persistence.models.retrieval_config import (
    RetrievalConfigurationModel,
)
from l1_support_bot.infrastructure.persistence.sqlalchemy.retrieval_config_repository import (
    SqlAlchemyRetrievalConfigRepository,
)


@pytest.mark.integration
async def test_configuration_snapshot_round_trips_atomically() -> None:
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)

    repository = SqlAlchemyRetrievalConfigRepository(
        async_sessionmaker(engine, expire_on_commit=False)
    )
    snapshot = ConfigurationSnapshot(
        llm=LLMConfig(provider="fake", model="test", endpoint="https://llm.test"),
        embedding=EmbeddingConfig(
            provider="fake",
            model="test",
            model_version="1",
            endpoint="https://embed.test",
            dimensions=3,
            index_compat_id="fake:test:1:3",
        ),
        retrieval=RetrievalConfig(),
        chunking=ChunkingConfig(),
    )

    await repository.save_all(snapshot)
    assert (await repository.get_llm()).model == "test"
    assert (await repository.get_embedding()).index_compat_id == "fake:test:1:3"
    assert (await repository.get_retrieval()).dense_weight == 0.7
    assert (await repository.get_chunking()).target_chunk_tokens == 512

    async with async_sessionmaker(engine, expire_on_commit=False)() as session:
        for model in (
            LLMConfigurationModel,
            EmbeddingConfigurationModel,
            RetrievalConfigurationModel,
            ChunkingConfigurationModel,
        ):
            rows = (await session.scalars(select(model).where(model.is_active.is_(True)))).all()
            assert len(rows) == 1
    await engine.dispose()
