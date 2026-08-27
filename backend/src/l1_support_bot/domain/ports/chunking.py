"""Structure-aware chunking contract."""

from collections.abc import Sequence
from typing import Protocol
from uuid import UUID

from l1_support_bot.domain.models.chunk import KnowledgeChunk
from l1_support_bot.domain.models.configuration import ChunkingConfig
from l1_support_bot.domain.models.parsed_document import ParsedDocument


class ChunkerPort(Protocol):
    async def chunk(
        self,
        parsed_document: ParsedDocument,
        config: ChunkingConfig,
        *,
        document_id: UUID | None = None,
        ingestion_job_id: UUID | None = None,
    ) -> Sequence[KnowledgeChunk]: ...
