from uuid import uuid4

from fastapi.testclient import TestClient

from l1_support_bot.domain.models.chunk import ChunkMetadata, KnowledgeChunk
from l1_support_bot.domain.models.configuration import EmbeddingConfig
from l1_support_bot.domain.ports.vector_store import VectorSearchResult
from l1_support_bot.interface.api.main import create_app
from l1_support_bot.interface.dependencies import PortDependencies


class Retriever:
    embedding_config = EmbeddingConfig(
        provider="fake", model="deterministic", model_version="1",
        endpoint="https://embedding.test", dimensions=3,
        index_compat_id="fake:deterministic:1:3",
    )

    async def retrieve(self, question, *, limit=5, filters=None, config=None):
        chunk = KnowledgeChunk.new(
            document_id=uuid4(), ingestion_job_id=uuid4(), sequence=0,
            text="Task code BA435 opens the customer account screen.",
            metadata=ChunkMetadata(document_name="manual.pdf", task_code="BA435"),
        )
        return (VectorSearchResult(chunk, 0.95),)


class LLM:
    async def complete(self, prompt, *, config):
        assert "REFERENCE MATERIAL" in prompt
        return '{"answer_text":"BA435 opens the customer account screen.","answer_type":"GROUNDED"}'


def test_chat_api_returns_grounded_answer_from_framed_context() -> None:
    app = create_app(dependencies=PortDependencies(retriever=Retriever(), llm=LLM()))
    response = TestClient(app).post(
        "/api/v1/chat",
        json={"question": "What is BA435?", "session_id": "00000000-0000-0000-0000-000000000001"},
    )

    assert response.status_code == 200
    assert response.json()["answer_type"] == "GROUNDED"
    assert response.json()["citations"][0]["task_code"] == "BA435"
