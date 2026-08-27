"""Last-valid runtime configuration cache used during relational outages."""

from __future__ import annotations

from l1_support_bot.application.configuration.runtime_health import RuntimeHealthState
from l1_support_bot.domain.errors import DatabaseUnavailableError
from l1_support_bot.domain.models.configuration import (
    ChunkingConfig,
    ConfigurationSnapshot,
    EmbeddingConfig,
    LLMConfig,
    RetrievalConfig,
)
from l1_support_bot.domain.ports.repositories import ConfigurationRepository


class InMemoryRuntimeConfigurationCache:
    def __init__(
        self,
        *,
        llm: LLMConfig | None = None,
        embedding: EmbeddingConfig | None = None,
        retrieval: RetrievalConfig | None = None,
        chunking: ChunkingConfig | None = None,
        repository: ConfigurationRepository | None = None,
        health: RuntimeHealthState | None = None,
    ) -> None:
        self._llm = llm
        self._embedding = embedding
        self._retrieval = retrieval
        self._chunking = chunking
        self.repository = repository
        self.health = health or RuntimeHealthState()

    @property
    def persistence_available(self) -> bool:
        return self.health.persistence_available

    @property
    def degraded_capabilities(self) -> list[str]:
        return self.health.degraded_capabilities

    async def get_llm(self) -> LLMConfig | None:
        return self._llm

    async def get_embedding(self) -> EmbeddingConfig | None:
        return self._embedding

    async def get_retrieval(self) -> RetrievalConfig | None:
        return self._retrieval

    async def get_chunking(self) -> ChunkingConfig | None:
        return self._chunking

    async def snapshot(self) -> ConfigurationSnapshot | None:
        if self._llm is None or self._embedding is None or self._retrieval is None:
            return None
        return ConfigurationSnapshot(
            llm=self._llm,
            embedding=self._embedding,
            retrieval=self._retrieval,
            chunking=self._chunking or ChunkingConfig(),
        )

    async def refresh(self) -> None:
        if self.repository is None:
            self.health.mark_normal()
            return
        try:
            llm = await self.repository.get_llm()
            embedding = await self.repository.get_embedding()
            retrieval = await self.repository.get_retrieval()
            get_chunking = getattr(self.repository, "get_chunking", None)
            chunking = await get_chunking() if get_chunking is not None else None
        except Exception as exc:
            self.health.mark_database(False)
            raise DatabaseUnavailableError() from exc
        if llm is not None:
            self._llm = llm
        if embedding is not None:
            self._embedding = embedding
        if retrieval is not None:
            self._retrieval = retrieval
        if chunking is not None:
            self._chunking = chunking
        self.health.mark_normal()

    def mark_component_unavailable(self, component: str) -> None:
        self.health.mark_component(component, False)

    def mark_component_available(self, component: str) -> None:
        self.health.mark_component(component, True)
