from uuid import uuid4

import pytest

from l1_support_bot.domain.models.chunk import ChunkMetadata, KnowledgeChunk
from l1_support_bot.infrastructure.vector_store.qdrant_store import QdrantVectorStore


def chunk(text: str, task_code: str | None = None) -> KnowledgeChunk:
    return KnowledgeChunk.new(
        document_id=uuid4(),
        ingestion_job_id=uuid4(),
        sequence=0,
        text=text,
        metadata=ChunkMetadata(document_name="manual.pdf", task_code=task_code),
        embedding_model_id="test:model:1:3",
    )


@pytest.mark.integration
@pytest.mark.asyncio
async def test_qdrant_local_store_upserts_searches_payload_and_checks_compatibility() -> None:
    try:
        from qdrant_client import QdrantClient
    except ImportError:
        pytest.skip("qdrant-client is not installed")

    client = QdrantClient(":memory:")
    store = QdrantVectorStore(client=client, collection_name="phase5-test", dimensions=3)
    item = chunk("Task code BA435 opens the customer account screen.", "BA435")

    await store.upsert((item,), ((1.0, 0.0, 0.0),))
    results = await store.search_dense((1.0, 0.0, 0.0), limit=5, filters={"task_code": "BA435"})

    assert results[0].chunk.metadata.task_code == "BA435"
    assert results[0].chunk.metadata.document_name == "manual.pdf"
    assert await store.is_compatible("test:model:1:3")
