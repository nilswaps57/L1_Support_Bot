"""Runtime configuration cache contract for degraded operation."""

from typing import Protocol

from l1_support_bot.domain.models.configuration import EmbeddingConfig, LLMConfig, RetrievalConfig


class RuntimeConfigurationCache(Protocol):
    async def get_llm(self) -> LLMConfig | None: ...

    async def get_embedding(self) -> EmbeddingConfig | None: ...

    async def get_retrieval(self) -> RetrievalConfig | None: ...

    async def refresh(self) -> None: ...
