import json
import re
from uuid import uuid4

from fastapi.testclient import TestClient

from l1_support_bot.domain.models.chunk import ChunkMetadata, KnowledgeChunk
from l1_support_bot.domain.models.configuration import EmbeddingConfig
from l1_support_bot.domain.models.ingestion import IngestionStatus
from l1_support_bot.domain.ports.vector_store import VectorSearchResult
from l1_support_bot.interface.api.main import create_app
from l1_support_bot.interface.dependencies import PortDependencies


class Retriever:
    embedding_config = EmbeddingConfig(
        provider="fake", model="deterministic", model_version="1", endpoint="https://embedding.test",
        dimensions=3, index_compat_id="fake:deterministic:1:3",
    )

    async def retrieve(self, question, *, limit=5, filters=None, config=None):
        return (
            VectorSearchResult(
                KnowledgeChunk.new(
                    document_id=uuid4(), ingestion_job_id=uuid4(), sequence=0,
                    text="BA435 opens the customer account screen.",
                    metadata=ChunkMetadata(document_name="task-codes.pdf", task_code="BA435"),
                ),
                0.95,
            ),
            VectorSearchResult(
                KnowledgeChunk.new(
                    document_id=uuid4(), ingestion_job_id=uuid4(), sequence=0,
                    text="The screen requires branch setup before use.",
                    metadata=ChunkMetadata(document_name="operations.pdf"),
                ),
                0.9,
            ),
        )


class LLM:
    async def complete(self, prompt, *, config):
        chunk_ids = re.findall(r"chunk_id=([0-9a-f-]+)", prompt)
        return json.dumps(
            {
                "answer_text": "BA435 opens the screen and requires branch setup.",
                "answer_type": "GROUNDED",
                "supported_chunk_ids": chunk_ids,
            }
        )


class Documents:
    async def get(self, document_id):
        return type("Document", (), {"id": document_id, "status": IngestionStatus.COMPLETED})()


def test_multi_source_chat_returns_each_materially_supporting_document() -> None:
    app = create_app(
        dependencies=PortDependencies(
            retriever=Retriever(), llm=LLM(), document_repository=Documents()
        )
    )

    response = TestClient(app).post(
        "/api/v1/chat",
        json={
            "question": "What does BA435 do and what setup does it require?",
            "session_id": str(uuid4()),
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["answer_type"] == "GROUNDED"
    assert {citation["document_name"] for citation in body["citations"]} == {
        "task-codes.pdf", "operations.pdf"
    }