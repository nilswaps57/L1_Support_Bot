from uuid import uuid4

import pytest

from l1_support_bot.domain.models.chunk import ChunkMetadata, KnowledgeChunk
from l1_support_bot.infrastructure.vector_store.qdrant_index_manager import QdrantIndexManager
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


@pytest.mark.integration
@pytest.mark.asyncio
async def test_generation_cutover_excludes_superseded_document_chunks() -> None:
    try:
        from qdrant_client import QdrantClient
    except ImportError:
        pytest.skip("qdrant-client is not installed")

    client = QdrantClient(":memory:")
    store = QdrantVectorStore(client=client, collection_name="generation-test", dimensions=3)
    manager = QdrantIndexManager(store)
    old = chunk("old task description", "BA435")
    other = chunk("unrelated task description", "BA436")
    replacement = KnowledgeChunk.new(
        document_id=old.document_id,
        ingestion_job_id=uuid4(),
        sequence=0,
        text="replacement task description",
        metadata=ChunkMetadata(document_name="manual-v2.pdf", task_code="BA435"),
        embedding_model_id="test:model:2:3",
    )

    await store.upsert((old, other), ((1.0, 0.0, 0.0), (0.0, 1.0, 0.0)))
    generation = await manager.begin_staging(
        old.document_id,
        embedding_model_id="test:model:2:3",
        chunking_config_id="chunk-v2",
    )
    await manager.stage(generation, (replacement,), ((1.0, 0.0, 0.0),))
    await manager.validate(
        generation,
        document_id=old.document_id,
        expected_chunks=1,
        embedding_model_id="test:model:2:3",
    )
    previous = await manager.cutover(generation)
    assert previous is not None
    await manager.cleanup(previous)

    results = await store.search_dense((1.0, 0.0, 0.0), limit=5)
    result_ids = {result.chunk.id for result in results}
    assert replacement.id in result_ids
    assert old.id not in result_ids
    assert other.id in result_ids
