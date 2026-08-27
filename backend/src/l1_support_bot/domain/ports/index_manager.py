"""Port for isolated index generations and atomic activation."""

from dataclasses import dataclass
from typing import Protocol
from uuid import UUID

from l1_support_bot.domain.models.chunk import KnowledgeChunk


@dataclass(frozen=True, slots=True)
class IndexGeneration:
    generation_id: str
    embedding_model_id: str
    chunking_config_id: str | None = None


class IndexManagerPort(Protocol):
    async def begin_staging(
        self,
        document_id: UUID,
        *,
        embedding_model_id: str,
        chunking_config_id: str | None,
    ) -> IndexGeneration: ...

    async def stage(
        self,
        generation: IndexGeneration,
        chunks: tuple[KnowledgeChunk, ...],
        vectors: tuple[tuple[float, ...], ...],
    ) -> None: ...

    async def validate(
        self,
        generation: IndexGeneration,
        *,
        document_id: UUID,
        expected_chunks: int,
        embedding_model_id: str,
    ) -> None: ...

    async def cutover(self, generation: IndexGeneration) -> IndexGeneration | None: ...

    async def rollback(self, generation: IndexGeneration) -> None: ...

    async def cleanup(self, generation: IndexGeneration) -> None: ...
