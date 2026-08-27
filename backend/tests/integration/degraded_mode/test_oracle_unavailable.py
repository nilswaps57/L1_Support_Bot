from types import SimpleNamespace
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from l1_support_bot.domain.errors import DatabaseUnavailableError
from l1_support_bot.domain.models.chunk import ChunkMetadata, KnowledgeChunk
from l1_support_bot.domain.models.configuration import EmbeddingConfig, LLMConfig, RetrievalConfig
from l1_support_bot.domain.ports.vector_store import VectorSearchResult
from l1_support_bot.infrastructure.configuration.runtime_config_cache import (
    InMemoryRuntimeConfigurationCache,
)
from l1_support_bot.interface.api.main import create_app
from l1_support_bot.interface.dependencies import PortDependencies


class FailingConfigurationRepository:
    def __init__(self) -> None:
        self.failed = True

    async def get_llm(self):
        if self.failed:
            raise RuntimeError("Oracle host=secret.internal password=hidden")
        return None

    async def get_embedding(self):
        if self.failed:
            raise RuntimeError("Oracle SQL details")
        return None

    async def get_retrieval(self):
        if self.failed:
            raise RuntimeError("filesystem /srv/metadata")
        return None


class IndexedRetriever:
    embedding_config = EmbeddingConfig(
        provider="fake",
        model="deterministic",
        model_version="1",
        endpoint="https://embedding.test",
        dimensions=3,
        index_compat_id="fake:deterministic:1:3",
    )

    async def retrieve(self, question, *, limit=5, filters=None, config=None):
        chunk = KnowledgeChunk.new(
            document_id=uuid4(),
            ingestion_job_id=uuid4(),
            sequence=0,
            text="BA435 opens the customer account screen.",
            metadata=ChunkMetadata(document_name="manual.md", task_code="BA435"),
        )
        return (VectorSearchResult(chunk, 0.95),)


class GroundingLLM:
    async def complete(self, prompt, *, config):
        import re

        chunk_id = re.search(r"chunk_id=([0-9a-f-]+)", prompt)
        assert chunk_id is not None
        return (
            '{"answer_text":"BA435 opens the customer account screen.",'
            f'"answer_type":"GROUNDED","supported_chunk_ids":["{chunk_id.group(1)}"]}}'
        )


@pytest.mark.asyncio
async def test_cache_preserves_last_valid_configuration_and_recovers() -> None:
    repository = FailingConfigurationRepository()
    cache = InMemoryRuntimeConfigurationCache(
        llm=LLMConfig(provider="fake", model="cached", endpoint="https://llm.test"),
        embedding=IndexedRetriever.embedding_config,
        retrieval=RetrievalConfig(),
        repository=repository,
    )

    with pytest.raises(DatabaseUnavailableError):
        await cache.refresh()
    assert not cache.persistence_available
    cached_llm = await cache.get_llm()
    assert cached_llm is not None
    assert cached_llm.model == "cached"
    repository.failed = False
    await cache.refresh()
    assert cache.persistence_available


def test_degraded_chat_uses_cached_configuration_and_skips_metadata_lookup() -> None:
    repository = FailingConfigurationRepository()
    cache = InMemoryRuntimeConfigurationCache(
        llm=LLMConfig(provider="fake", model="cached", endpoint="https://llm.test"),
        embedding=IndexedRetriever.embedding_config,
        retrieval=RetrievalConfig(),
        repository=repository,
    )
    app = create_app(
        dependencies=PortDependencies(
            retriever=IndexedRetriever(),
            llm=GroundingLLM(),
            document_repository=SimpleNamespace(
                get=lambda document_id: (_ for _ in ()).throw(AssertionError("not queried"))
            ),
            runtime_configuration_cache=cache,
        )
    )

    response = TestClient(app).post(
        "/api/v1/chat", json={"session_id": str(uuid4()), "question": "What is BA435?"}
    )

    assert response.status_code == 200
    assert response.json()["answer_type"] == "GROUNDED"
    health = TestClient(app).get("/api/v1/health").json()
    assert health["status"] == "degraded"
    assert "document_management" in health["degraded_capabilities"]
    assert health["capabilities"]["chat"] is True
