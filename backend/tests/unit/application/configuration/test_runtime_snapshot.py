import pytest

from l1_support_bot.domain.models.configuration import (
    ChunkingConfig,
    EmbeddingConfig,
    LLMConfig,
    RetrievalConfig,
)
from l1_support_bot.infrastructure.configuration.runtime_config_cache import (
    InMemoryRuntimeConfigurationCache,
)


class Repository:
    def __init__(self) -> None:
        self.llm = LLMConfig(provider="fake", model="old", endpoint="https://llm.test")
        self.embedding = EmbeddingConfig(
            provider="fake", model="embed", model_version="1", endpoint="https://embed.test",
            dimensions=3, index_compat_id="fake:embed:1:3",
        )
        self.retrieval = RetrievalConfig()
        self.chunking = ChunkingConfig()

    async def get_llm(self) -> LLMConfig:
        return self.llm

    async def get_embedding(self) -> EmbeddingConfig:
        return self.embedding

    async def get_retrieval(self) -> RetrievalConfig:
        return self.retrieval

    async def get_chunking(self) -> ChunkingConfig:
        return self.chunking


@pytest.mark.asyncio
async def test_in_flight_snapshot_does_not_change_during_refresh() -> None:
    repository = Repository()
    cache = InMemoryRuntimeConfigurationCache(
        llm=repository.llm, embedding=repository.embedding,
        retrieval=repository.retrieval, chunking=repository.chunking,
        repository=repository,
    )
    before = await cache.snapshot()
    repository.llm = LLMConfig(provider="fake", model="new", endpoint="https://llm.test")

    await cache.refresh()
    after = await cache.snapshot()

    assert before is not None
    assert after is not None
    assert before.llm.model == "old"
    assert after.llm.model == "new"