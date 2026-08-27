import json
import re
from uuid import uuid4

import pytest

from l1_support_bot.application.retrieval.ask_question import AskQuestion
from l1_support_bot.domain.models.answer import AnswerType
from l1_support_bot.domain.models.chunk import ChunkMetadata, KnowledgeChunk
from l1_support_bot.domain.models.configuration import EmbeddingConfig, LLMConfig, RetrievalConfig
from l1_support_bot.domain.models.ingestion import IngestionStatus
from l1_support_bot.domain.ports.vector_store import VectorSearchResult


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

    async def retrieve(self, question: str, *, limit: int, config: RetrievalConfig):
        return self.results


class LLM:
    def __init__(self, answer_type: str, answer_text: str) -> None:
        self.answer_type = answer_type
        self.answer_text = answer_text
        self.calls = 0

    async def complete(self, prompt: str, *, config: LLMConfig) -> str:
        self.calls += 1
        chunk_id = re.search(r"chunk_id=([0-9a-f-]+)", prompt)
        supported = [chunk_id.group(1)] if chunk_id else []
        return json.dumps(
            {
                "answer_text": self.answer_text,
                "answer_type": self.answer_type,
                "supported_chunk_ids": supported,
            }
        )


class Documents:
    async def get(self, document_id):
        return type("Document", (), {"id": document_id, "status": IngestionStatus.COMPLETED})()


def result(text: str, *, task_code: str | None = None) -> VectorSearchResult:
    document_id = uuid4()
    return VectorSearchResult(
        KnowledgeChunk.new(
            document_id=document_id,
            ingestion_job_id=uuid4(),
            sequence=0,
            text=text,
            metadata=ChunkMetadata(document_name="manual.md", task_code=task_code),
        ),
        0.95,
    )


def llm_config() -> LLMConfig:
    return LLMConfig(provider="fake", model="test", endpoint="https://llm.test")


@pytest.mark.asyncio
async def test_unsupported_question_returns_insufficient_without_calling_llm() -> None:
    llm = LLM("GROUNDED", "This must never be returned.")
    answer = await AskQuestion(retriever=Retriever(()), llm=llm, llm_config=llm_config()).execute(
        "What is quantum computing in FLEXCUBE?"
    )

    assert answer.answer_type is AnswerType.INSUFFICIENT
    assert answer.insufficient_information is True
    assert answer.citations == ()
    assert llm.calls == 0


@pytest.mark.asyncio
async def test_incorrect_identifier_premise_is_explicit_and_uncited() -> None:
    supporting = result("BA435 opens the customer account screen.", task_code="BA435")
    llm = LLM("GROUNDED", "This must never be returned.")
    answer = await AskQuestion(
        retriever=Retriever((supporting,)),
        llm=llm,
        llm_config=llm_config(),
        document_repository=Documents(),
    ).execute("Why does screen BA999 open the customer account?")

    assert answer.answer_type is AnswerType.INCORRECT_PREMISE
    assert "not supported" in answer.answer_text
    assert answer.citations == ()
    assert llm.calls == 0


@pytest.mark.asyncio
async def test_partial_answer_cites_only_supported_chunk() -> None:
    supporting = result(
        "BA435 opens the customer account screen and requires branch code. The "
        "approval workflow is not described.",
        task_code="BA435",
    )
    llm = LLM("PARTIAL", "BA435 opens the screen; the approval workflow is not covered.")
    answer = await AskQuestion(
        retriever=Retriever((supporting,)),
        llm=llm,
        llm_config=llm_config(),
        document_repository=Documents(),
    ).execute("What does BA435 do and what is its approval workflow?")

    assert answer.answer_type is AnswerType.PARTIAL
    assert len(answer.citations) == 1
    assert answer.citations[0].chunk_id == supporting.chunk.id


@pytest.mark.asyncio
async def test_ambiguous_answer_is_uncited() -> None:
    first = result("BA435 opens the customer account screen.", task_code="BA435")
    second = result("BA436 opens the customer maintenance screen.", task_code="BA436")
    llm = LLM("AMBIGUOUS", "The question could refer to BA435 or BA436; please clarify.")
    answer = await AskQuestion(
        retriever=Retriever((first, second)),
        llm=llm,
        llm_config=llm_config(),
        retrieval_config=RetrievalConfig(min_evidence_tokens=1),
        document_repository=Documents(),
    ).execute("Which account screen should I use?")

    assert answer.answer_type is AnswerType.AMBIGUOUS
    assert answer.citations == ()
