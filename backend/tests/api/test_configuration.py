from typing import Any

from fastapi.testclient import TestClient

from l1_support_bot.domain.models.configuration import (
    ChunkingConfig,
    EmbeddingConfig,
    LLMConfig,
    RetrievalConfig,
)
from l1_support_bot.infrastructure.configuration.runtime_config_cache import (
    InMemoryRuntimeConfigurationCache,
)
from l1_support_bot.interface.api.main import create_app
from l1_support_bot.interface.dependencies import PortDependencies


class MemoryConfigurationRepository:
    def __init__(self, *, indexed_documents: int = 0) -> None:
        self.llm = LLMConfig(provider="fake", model="old", endpoint="https://llm.test")
        self.embedding = EmbeddingConfig(
            provider="fake",
            model="old",
            model_version="1",
            endpoint="https://embed.test",
            dimensions=3,
            index_compat_id="fake:old:1:3",
        )
        self.retrieval = RetrievalConfig()
        self.chunking = ChunkingConfig()
        self.indexed_documents = indexed_documents
        self.saved = 0

    async def get_llm(self) -> LLMConfig:
        return self.llm

    async def get_embedding(self) -> EmbeddingConfig:
        return self.embedding

    async def get_retrieval(self) -> RetrievalConfig:
        return self.retrieval

    async def get_chunking(self) -> ChunkingConfig:
        return self.chunking

    async def count_indexed_documents(self) -> int:
        return self.indexed_documents

    async def save_all(self, configuration: Any) -> None:
        self.llm = configuration.llm
        self.embedding = configuration.embedding
        self.retrieval = configuration.retrieval
        self.chunking = configuration.chunking
        self.saved += 1

    async def save_llm(self, config: LLMConfig) -> LLMConfig:
        self.llm = config
        return config

    async def save_embedding(self, config: EmbeddingConfig) -> EmbeddingConfig:
        self.embedding = config
        return config

    async def save_retrieval(self, config: RetrievalConfig) -> RetrievalConfig:
        self.retrieval = config
        return config

    async def save_chunking(self, config: ChunkingConfig) -> ChunkingConfig:
        self.chunking = config
        return config


class HealthyLLM:
    async def health_check(self, *, config: LLMConfig) -> bool:
        return config.model != "unreachable"


class HealthyEmbedding:
    async def embed_query(self, text: str, config: EmbeddingConfig) -> tuple[float, ...]:
        return (0.1,) * config.dimensions


def make_client(
    repository: MemoryConfigurationRepository | None = None,
    *,
    llm: object | None = None,
    embedding: object | None = None,
) -> tuple[TestClient, MemoryConfigurationRepository]:
    resolved = repository or MemoryConfigurationRepository()
    cache = InMemoryRuntimeConfigurationCache(
        llm=resolved.llm,
        embedding=resolved.embedding,
        retrieval=resolved.retrieval,
        repository=resolved,
    )
    return (
        TestClient(
            create_app(
                dependencies=PortDependencies(
                    configuration_repository=resolved,
                    runtime_configuration_cache=cache,
                    llm=llm or HealthyLLM(),
                    embedding=embedding or HealthyEmbedding(),
                )
            )
        ),
        resolved,
    )


def test_configuration_reads_never_return_secret_or_internal_ids() -> None:
    client, _ = make_client()

    response = client.get("/api/v1/config/llm")

    assert response.status_code == 200
    payload = response.json()
    assert payload["model"] == "old"
    assert "api_key" not in payload
    assert "endpoint" not in payload
    assert "config_id" not in payload


def test_valid_retrieval_update_is_active_and_invalid_update_does_not_replace_it() -> None:
    client, repository = make_client()

    response = client.put(
        "/api/v1/config/retrieval",
        json={"top_k_candidates": 10, "final_top_k": 4, "dense_weight": 0.6, "sparse_weight": 0.4},
    )
    assert response.status_code == 200
    assert response.json()["status"] == "active"
    assert repository.retrieval.top_k_candidates == 10

    rejected = client.put(
        "/api/v1/config/retrieval",
        json={"top_k_candidates": 2, "final_top_k": 3, "dense_weight": 0.6, "sparse_weight": 0.4},
    )
    assert rejected.status_code in {400, 422}
    assert repository.retrieval.top_k_candidates == 10


def test_unreachable_llm_is_rejected_without_persisting() -> None:
    client, repository = make_client()

    response = client.put(
        "/api/v1/config/llm",
        json={"provider": "fake", "model": "unreachable", "endpoint": "https://safe.test"},
    )

    assert response.status_code == 422
    assert response.json()["error_code"] == "LLM_CONNECTIVITY_FAILED"
    assert repository.saved == 0
    assert repository.llm.model == "old"
    assert "safe.test" not in response.text


def test_embedding_change_is_blocked_when_index_exists() -> None:
    client, repository = make_client(MemoryConfigurationRepository(indexed_documents=2))

    response = client.put(
        "/api/v1/config/embedding",
        json={
            "provider": "fake",
            "model": "new",
            "model_version": "1",
            "dimensions": 3,
            "index_compat_id": "fake:new:1:3",
        },
    )

    assert response.status_code == 409
    assert response.json()["error_code"] == "REINDEX_REQUIRED"
    assert repository.embedding.model == "old"


def test_mutations_are_blocked_when_authoritative_persistence_is_unavailable() -> None:
    repository = MemoryConfigurationRepository()
    cache = InMemoryRuntimeConfigurationCache(repository=repository)

    async def unavailable() -> LLMConfig:
        raise RuntimeError("database secret")

    repository.get_llm = unavailable  # type: ignore[method-assign]
    client = TestClient(
        create_app(
            dependencies=PortDependencies(
                configuration_repository=repository,
                runtime_configuration_cache=cache,
            )
        )
    )

    response = client.put(
        "/api/v1/config/retrieval",
        json={"top_k_candidates": 10, "final_top_k": 4, "dense_weight": 0.6, "sparse_weight": 0.4},
    )

    assert response.status_code == 503
    assert response.json()["error_code"] == "DATABASE_UNAVAILABLE"
    assert "database secret" not in response.text
