import re
from types import SimpleNamespace
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
        provider="fake",
        model="deterministic",
        model_version="1",
        endpoint="https://embedding.test",
        dimensions=3,
        index_compat_id="fake:deterministic:1:3",
    )

    def __init__(self, results: tuple[VectorSearchResult, ...]) -> None:
        self.results = results

    async def retrieve(self, question, *, limit=5, filters=None, config=None):
        return self.results


class LLM:
    def __init__(self, answer_type: str = "GROUNDED") -> None:
        self.answer_type = answer_type

    async def complete(self, prompt, *, config):
        if self.answer_type == "INSUFFICIENT":
            return '{"answer_text":"No supporting evidence.","answer_type":"INSUFFICIENT"}'
        chunk_id = re.search(r"chunk_id=([0-9a-f-]+)", prompt)
        assert chunk_id is not None
        return (
            '{"answer_text":"The source answer.","answer_type":"GROUNDED",'
            f'"supported_chunk_ids":["{chunk_id.group(1)}"]}}'
        )


class Documents:
    def __init__(self, statuses: dict) -> None:
        self.statuses = statuses

    async def get(self, document_id):
        status = self.statuses.get(document_id)
        return SimpleNamespace(id=document_id, status=status) if status else None


def make_result(*, page_number: int | None) -> VectorSearchResult:
    document_id = uuid4()
    chunk = KnowledgeChunk.new(
        document_id=document_id,
        ingestion_job_id=uuid4(),
        sequence=0,
        text="BA435 opens the customer account screen.",
        metadata=ChunkMetadata(
            document_name="FLEXCUBE Manual",
            page_number=page_number,
            section="Task Codes > BA435",
            task_code="BA435",
        ),
    )
    return VectorSearchResult(chunk, 0.9)


def test_grounded_response_preserves_citation_and_omits_missing_page() -> None:
    result = make_result(page_number=None)
    app = create_app(
        dependencies=PortDependencies(
            retriever=Retriever((result,)),
            llm=LLM(),
            document_repository=Documents({result.chunk.document_id: IngestionStatus.COMPLETED}),
        )
    )

    response = TestClient(app).post(
        "/api/v1/chat",
        json={"question": "What is BA435?", "session_id": str(uuid4())},
    )

    assert response.status_code == 200
    citation = response.json()["citations"][0]
    assert citation["document_name"] == "FLEXCUBE Manual"
    assert citation["section"] == "Task Codes > BA435"
    assert citation["task_code"] == "BA435"
    assert "page_number" not in citation


def test_insufficient_response_has_no_citations() -> None:
    app = create_app(dependencies=PortDependencies(retriever=Retriever(()), llm=LLM()))

    response = TestClient(app).post(
        "/api/v1/chat",
        json={"question": "What is undocumented?", "session_id": str(uuid4())},
    )

    assert response.status_code == 200
    assert response.json()["answer_type"] == "INSUFFICIENT"
    assert response.json()["citations"] == []
    assert response.json()["insufficient_information"] is True


def test_deleted_retrieved_document_is_not_cited() -> None:
    result = make_result(page_number=12)
    app = create_app(
        dependencies=PortDependencies(
            retriever=Retriever((result,)),
            llm=LLM(),
            document_repository=Documents({result.chunk.document_id: IngestionStatus.DELETED}),
        )
    )

    response = TestClient(app).post(
        "/api/v1/chat",
        json={"question": "What is BA435?", "session_id": str(uuid4())},
    )

    assert response.status_code == 200
    assert response.json()["answer_type"] == "INSUFFICIENT"
    assert response.json()["citations"] == []