"""Retrieval and result ranking contracts."""

from collections.abc import Mapping, Sequence
from typing import Protocol

from l1_support_bot.domain.models.configuration import RetrievalConfig
from l1_support_bot.domain.ports.reranker import RerankerPort
from l1_support_bot.domain.ports.vector_store import VectorSearchResult

__all__ = ["RerankerPort", "RetrieverPort"]


class RetrieverPort(Protocol):
    async def retrieve(
        self,
        question: str,
        *,
        limit: int = 5,
        filters: Mapping[str, str] | None = None,
        config: RetrievalConfig | None = None,
    ) -> Sequence[VectorSearchResult]: ...
