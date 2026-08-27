"""Runtime configuration cache contract for degraded operation."""

from typing import Protocol

from l1_support_bot.domain.models.configuration import (
    ChunkingConfig,
    ConfigurationSnapshot,
    EmbeddingConfig,
    LLMConfig,
    RetrievalConfig,
)


class RuntimeConfigurationCache(Protocol):
    async def get_llm(self) -> LLMConfig | None: ...

    async def get_embedding(self) -> EmbeddingConfig | None: ...

    async def get_retrieval(self) -> RetrievalConfig | None: ...

    async def get_chunking(self) -> ChunkingConfig | None: ...

    async def snapshot(self) -> ConfigurationSnapshot | None: ...

    async def refresh(self) -> None: ...

    @property
    def persistence_available(self) -> bool: ...

    @property
    def degraded_capabilities(self) -> list[str]: ...
