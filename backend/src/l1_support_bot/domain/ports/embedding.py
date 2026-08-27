"""Embedding provider contract."""

from collections.abc import Sequence
from typing import Protocol

from l1_support_bot.domain.models.configuration import EmbeddingConfig


class EmbeddingPort(Protocol):
    async def embed_batch(
        self,
        texts: Sequence[str],
        config: EmbeddingConfig,
    ) -> Sequence[Sequence[float]]: ...

    async def embed_query(self, text: str, config: EmbeddingConfig) -> Sequence[float]: ...
