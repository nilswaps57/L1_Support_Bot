"""Vector index contract."""

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Protocol
from uuid import UUID

from l1_support_bot.domain.models.chunk import KnowledgeChunk


@dataclass(frozen=True, slots=True)
class VectorSearchResult:
    chunk: KnowledgeChunk
    score: float


class VectorStorePort(Protocol):
    async def upsert(
        self,
        chunks: Sequence[KnowledgeChunk],
        vectors: Sequence[Sequence[float]],
    ) -> None: ...

    async def search_dense(
        self,
        vector: Sequence[float],
        *,
        limit: int,
        filters: Mapping[str, str] | None = None,
    ) -> Sequence[VectorSearchResult]: ...

    async def search_sparse(
        self,
        terms: Sequence[str],
        *,
        limit: int,
        filters: Mapping[str, str] | None = None,
    ) -> Sequence[VectorSearchResult]: ...

    async def delete_by_document(self, document_id: UUID) -> None: ...

    async def is_compatible(self, embedding_model_id: str) -> bool: ...


VectorStore = VectorStorePort
