from types import SimpleNamespace
from uuid import uuid4

from fastapi.testclient import TestClient

from l1_support_bot.domain.errors import (
    DatabaseUnavailableError,
    EmbeddingUnavailableError,
    LLMUnavailableError,
    VectorStoreUnavailableError,
)
from l1_support_bot.domain.models.chunk import ChunkMetadata, KnowledgeChunk
from l1_support_bot.domain.models.configuration import EmbeddingConfig
from l1_support_bot.domain.ports.vector_store import VectorSearchResult
from l1_support_bot.interface.api.main import create_app
from l1_support_bot.interface.dependencies import PortDependencies


class Retriever:
    embedding_config = EmbeddingConfig(
        provider="fake",
        model="deterministic",
        model_version="1",
        endpoint="https://embedding.test",
        dimensions=3,
        index_compat_id="fake:deterministic:1:3",
    )

    def __init__(self, failure: Exception | None = None) -> None:
        self.failure = failure

    async def retrieve(self, question, *, limit=5, filters=None, config=None):
        if self.failure:
            raise self.failure
        chunk = KnowledgeChunk.new(
            document_id=uuid4(),
            ingestion_job_id=uuid4(),
            sequence=0,
            text="BA435 opens the customer account screen.",
            metadata=ChunkMetadata(document_name="manual.md", task_code="BA435"),
        )
        return (VectorSearchResult(chunk, 0.95),)


class Documents:
    def __init__(self, failure: Exception | None = None) -> None:
        self.failure = failure

    async def get(self, document_id):
        if self.failure:
            raise self.failure
        return SimpleNamespace(id=document_id, status="COMPLETED")


class LLM:
    def __init__(self, failure: Exception | None = None) -> None:
        self.failure = failure

    async def complete(self, prompt, *, config):
        if self.failure:
            raise self.failure
        return (
            '{"answer_text":"BA435 opens the customer account screen.",'
            '"answer_type":"GROUNDED","supported_chunk_ids":[]}'
        )


def post(app, question: str = "What is undocumented?"):
    return TestClient(app).post(
        "/api/v1/chat",
        json={"question": question, "session_id": str(uuid4())},
    )


def test_absent_evidence_is_a_successful_explicit_insufficient_response() -> None:
    response = post(create_app(dependencies=PortDependencies(retriever=Retriever(), llm=LLM())))

    assert response.status_code == 200
    assert response.json()["answer_type"] == "INSUFFICIENT"
    assert response.json()["citations"] == []


def test_llm_failure_is_distinct_from_insufficient_evidence() -> None:
    app = create_app(
        dependencies=PortDependencies(
            retriever=Retriever(), llm=LLM(LLMUnavailableError("LLM is unavailable."))
        )
    )
    response = post(app, "What is task code BA435?")

    assert response.status_code == 503
    assert response.json()["error_code"] == "LLM_UNAVAILABLE"


def test_vector_store_failure_is_distinct_from_insufficient_evidence() -> None:
    app = create_app(
        dependencies=PortDependencies(
            retriever=Retriever(VectorStoreUnavailableError("Vector store is unavailable.")),
            llm=LLM(),
        )
    )
    response = post(app)

    assert response.status_code == 503
    assert response.json()["error_code"] == "VECTOR_STORE_UNAVAILABLE"


def test_embedding_failure_is_distinct_from_insufficient_evidence() -> None:
    app = create_app(
        dependencies=PortDependencies(
            retriever=Retriever(EmbeddingUnavailableError("Embedding is unavailable.")), llm=LLM()
        )
    )
    response = post(app)

    assert response.status_code == 503
    assert response.json()["error_code"] == "EMBEDDING_UNAVAILABLE"


def test_database_failure_is_distinct_from_insufficient_evidence() -> None:
    app = create_app(
        dependencies=PortDependencies(
            retriever=Retriever(),
            llm=LLM(),
            document_repository=Documents(DatabaseUnavailableError("Database is unavailable.")),
        )
    )
    response = post(app, "What is task code BA435?")

    assert response.status_code == 503
    assert response.json()["error_code"] == "DATABASE_UNAVAILABLE"
