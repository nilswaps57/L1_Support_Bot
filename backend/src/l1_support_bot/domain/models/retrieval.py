"""Retrieval result and grounded-context value objects."""

from dataclasses import dataclass
from uuid import UUID

from l1_support_bot.domain.models.chunk import KnowledgeChunk


@dataclass(frozen=True, slots=True)
class RetrievedChunk:
    chunk: KnowledgeChunk
    score: float
    source: str = "dense"

    @property
    def chunk_id(self) -> UUID:
        return self.chunk.id


@dataclass(frozen=True, slots=True)
class ContextChunk:
    chunk: KnowledgeChunk
    score: float
    ordinal: int
