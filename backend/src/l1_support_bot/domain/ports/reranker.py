"""Replaceable candidate reranking contract."""

from collections.abc import Sequence
from typing import Protocol

from l1_support_bot.domain.ports.vector_store import VectorSearchResult


class RerankerPort(Protocol):
    async def rerank(
        self,
        question: str,
        candidates: Sequence[VectorSearchResult],
        *,
        limit: int,
    ) -> Sequence[VectorSearchResult]: ...