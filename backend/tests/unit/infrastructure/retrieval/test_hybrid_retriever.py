from uuid import uuid4

import pytest

from l1_support_bot.domain.models.chunk import ChunkMetadata, KnowledgeChunk
from l1_support_bot.domain.models.configuration import RetrievalConfig
from l1_support_bot.domain.ports.vector_store import VectorSearchResult
from l1_support_bot.infrastructure.retrieval.hybrid_retriever import HybridRetriever


def result(text: str, score: float, task: str | None = None) -> VectorSearchResult:
    return VectorSearchResult(
        KnowledgeChunk.new(
            document_id=uuid4(), ingestion_job_id=uuid4(), sequence=0, text=text,
            metadata=ChunkMetadata(document_name="manual", task_code=task),
        ), score,
    )


class Store:
    async def search_dense(self, vector, *, limit, filters=None):
        return (result("general account screen", 0.7), result("BA435 account screen", 0.6, "BA435"))

    async def search_sparse(self, terms, *, limit, filters=None):
        return (result("BA435 account screen", 0.9, "BA435"), result("general account screen", 0.5))

    async def is_compatible(self, embedding_model_id):
        return True

    async def upsert(self, chunks, vectors):
        return None

    async def delete_by_document(self, document_id):
        return None


class Embedding:
    async def embed_query(self, text, config):
        return (1.0, 0.0)


@pytest.mark.asyncio
async def test_hybrid_retriever_fuses_dense_sparse_exact_identifier_and_deduplicates() -> None:
    retriever = HybridRetriever(
        vector_store=Store(), embedding=Embedding(), embedding_config=_config()
    )
    results = await retriever.retrieve("What is BA435?", config=RetrievalConfig(final_top_k=2))

    assert len(results) == 2
    assert results[0].chunk.metadata.task_code == "BA435"


def _config():
    from l1_support_bot.domain.models.configuration import EmbeddingConfig

    return EmbeddingConfig(
        provider="fake", model="test", model_version="1", endpoint="https://test",
        dimensions=2, index_compat_id="fake:test:1:2",
    )
