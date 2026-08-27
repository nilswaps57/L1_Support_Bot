"""Persistence contracts owned by the domain boundary."""

from collections.abc import Sequence
from typing import Protocol
from uuid import UUID

from l1_support_bot.domain.models.chunk import KnowledgeChunk
from l1_support_bot.domain.models.configuration import (
    ChunkingConfig,
    EmbeddingConfig,
    LLMConfig,
    RetrievalConfig,
)
from l1_support_bot.domain.models.document import Document, SourceType
from l1_support_bot.domain.models.feedback import Feedback
from l1_support_bot.domain.models.ingestion import IngestionJob, IngestionStatus


class DocumentRepository(Protocol):
    async def get(self, document_id: UUID) -> Document | None: ...

    async def get_by_checksum(self, checksum: str) -> Document | None: ...

    async def save(self, document: Document) -> Document: ...

    async def list(
        self,
        *,
        status: IngestionStatus | None = None,
        source_type: SourceType | None = None,
    ) -> Sequence[Document]: ...

    async def update_status(self, document_id: UUID, status: IngestionStatus) -> Document: ...

    async def delete(self, document_id: UUID) -> None: ...


class IngestionJobRepository(Protocol):
    async def create(self, job: IngestionJob) -> IngestionJob: ...

    async def get(self, job_id: UUID) -> IngestionJob | None: ...

    async def update(self, job: IngestionJob) -> IngestionJob: ...

    async def list_pending(self, *, limit: int = 10) -> Sequence[IngestionJob]: ...

    async def latest_for_document(self, document_id: UUID) -> IngestionJob | None: ...


class ChunkRepository(Protocol):
    async def save_batch(self, chunks: Sequence[KnowledgeChunk]) -> None: ...

    async def delete_by_document(self, document_id: UUID) -> None: ...


class FeedbackRepository(Protocol):
    async def save(self, feedback: Feedback) -> Feedback: ...

    async def list_by_session(self, session_id: UUID) -> Sequence[Feedback]: ...


class ConfigurationRepository(Protocol):
    async def get_llm(self) -> LLMConfig | None: ...

    async def get_embedding(self) -> EmbeddingConfig | None: ...

    async def get_retrieval(self) -> RetrievalConfig | None: ...

    async def get_chunking(self) -> ChunkingConfig | None: ...

    async def save_llm(self, config: LLMConfig) -> LLMConfig: ...

    async def save_embedding(self, config: EmbeddingConfig) -> EmbeddingConfig: ...

    async def save_retrieval(self, config: RetrievalConfig) -> RetrievalConfig: ...

    async def save_chunking(self, config: ChunkingConfig) -> ChunkingConfig: ...
