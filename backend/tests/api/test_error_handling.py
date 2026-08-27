from uuid import uuid4

from fastapi.testclient import TestClient

from l1_support_bot.domain.models.configuration import EmbeddingConfig, LLMConfig
from l1_support_bot.infrastructure.configuration.runtime_config_cache import (
    InMemoryRuntimeConfigurationCache,
)
from l1_support_bot.interface.api.main import create_app
from l1_support_bot.interface.dependencies import PortDependencies


class FailingRetriever:
    embedding_config = EmbeddingConfig(
        provider="fake",
        model="deterministic",
        model_version="1",
        endpoint="https://embedding.test",
        dimensions=3,
        index_compat_id="fake:deterministic:1:3",
    )

    async def retrieve(self, question, *, limit=5, filters=None, config=None):
        raise RuntimeError(
            "Traceback /home/service/app.py credentials=secret endpoint=http://internal SQL select"
        )


class UnavailableConfigurationRepository:
    async def get_llm(self):
        raise RuntimeError("Oracle password=secret")

    async def get_embedding(self):
        raise RuntimeError("Oracle password=secret")

    async def get_retrieval(self):
        raise RuntimeError("Oracle password=secret")


def test_unexpected_retrieval_failure_is_sanitized_and_has_request_id() -> None:
    response = TestClient(
        create_app(dependencies=PortDependencies(retriever=FailingRetriever(), llm=object()))
    ).post(
        "/api/v1/chat", json={"session_id": str(uuid4()), "question": "What is BA435?"}
    )

    assert response.status_code == 503
    payload = response.json()
    assert payload["error_code"] == "VECTOR_STORE_UNAVAILABLE"
    assert response.headers["x-request-id"] == payload["request_id"]
    assert all(
        secret not in response.text
        for secret in ("Traceback", "/home/service", "credentials", "internal", "SQL")
    )


def test_degraded_health_exposes_capabilities_without_infrastructure_details() -> None:
    cache = InMemoryRuntimeConfigurationCache(repository=UnavailableConfigurationRepository())
    app = create_app(dependencies=PortDependencies(runtime_configuration_cache=cache))
    response = TestClient(app).get("/api/v1/health")

    assert response.status_code == 200
    payload = response.json()
    assert set(payload) >= {"status", "degraded_capabilities", "capabilities"}
    assert payload["status"] == "degraded"
    assert "password" not in response.text


def test_configuration_mutation_is_rejected_while_persistence_is_unavailable() -> None:
    cache = InMemoryRuntimeConfigurationCache(
        llm=LLMConfig(provider="fake", model="cached", endpoint="https://llm.test"),
        repository=UnavailableConfigurationRepository(),
    )
    response = TestClient(
        create_app(dependencies=PortDependencies(runtime_configuration_cache=cache))
    ).put(
        "/api/v1/config/retrieval",
        json={
            "top_k_candidates": 20,
            "final_top_k": 5,
            "similarity_threshold": 0.4,
            "dense_weight": 0.7,
            "sparse_weight": 0.3,
            "rerank_enabled": False,
            "rerank_top_k": 20,
            "exact_id_boost": True,
            "min_evidence_tokens": 100,
        },
    )

    assert response.status_code == 503
    assert response.json()["error_code"] == "DATABASE_UNAVAILABLE"
