from uuid import uuid4

import pytest

from l1_support_bot.domain.models.chunk import ChunkMetadata, KnowledgeChunk
from l1_support_bot.infrastructure.retrieval.lexical_retriever import LexicalRetriever


def make_chunk(text: str) -> KnowledgeChunk:
    return KnowledgeChunk.new(
        document_id=uuid4(), ingestion_job_id=uuid4(), sequence=0, text=text,
        metadata=ChunkMetadata(document_name="manual"),
    )


@pytest.mark.asyncio
async def test_bm25_prioritizes_exact_technical_terms() -> None:
    exact = make_chunk("BA435 customer account screen procedure")
    broad = make_chunk("customer account screen overview")

    results = await LexicalRetriever((broad, exact)).retrieve("BA435 screen", limit=2)

    assert results[0].chunk.id == exact.id
