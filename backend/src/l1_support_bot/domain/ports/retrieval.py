"""Retrieval and result ranking contracts."""

from collections.abc import Mapping, Sequence
from typing import Protocol

from l1_support_bot.domain.models.configuration import RetrievalConfig
from l1_support_bot.domain.ports.vector_store import VectorSearchResult


class RetrieverPort(Protocol):
    async def retrieve(
        self,
        question: str,
        *,
        limit: int = 5,
        filters: Mapping[str, str] | None = None,
        config: RetrievalConfig | None = None,
    ) -> Sequence[VectorSearchResult]: ...


class RerankerPort(Protocol):
    async def rerank(
        self,
        question: str,
        candidates: Sequence[VectorSearchResult],
        *,
        limit: int,
    ) -> Sequence[VectorSearchResult]: ...
