import json
from uuid import uuid4

import pytest

from l1_support_bot.application.retrieval.ask_question import AskQuestion
from l1_support_bot.domain.models.answer import AnswerType
from l1_support_bot.domain.models.chunk import ChunkMetadata, KnowledgeChunk
from l1_support_bot.domain.models.configuration import LLMConfig, RetrievalConfig
from l1_support_bot.domain.ports.vector_store import VectorSearchResult


def make_result(
    text: str,
    *,
    document_name: str,
    screen_name: str | None = None,
) -> VectorSearchResult:
    chunk = KnowledgeChunk.new(
        document_id=uuid4(),
        ingestion_job_id=uuid4(),
        sequence=0,
        text=text,
        metadata=ChunkMetadata(document_name=document_name, screen_name=screen_name),
    )
    return VectorSearchResult(chunk, 0.95)


class Retriever:
    def __init__(self, results: tuple[VectorSearchResult, ...]) -> None:
        self.results = results
        self.queries: list[str] = []

    async def retrieve(self, question: str, *, limit: int, config: RetrievalConfig):
        self.queries.append(question)
        return self.results


class JsonLLM:
    def __init__(self, payload: dict[str, object]) -> None:
        self.payload = payload

    async def complete(self, prompt: str, *, config: LLMConfig) -> str:
        return json.dumps(self.payload)


def ask(results: tuple[VectorSearchResult, ...], payload: dict[str, object]) -> AskQuestion:
    return AskQuestion(
        retriever=Retriever(results),
        llm=JsonLLM(payload),
        llm_config=LLMConfig(provider="fake", model="test", endpoint="https://llm.test"),
        retrieval_config=RetrievalConfig(min_evidence_tokens=1),
    )


@pytest.mark.asyncio
async def test_partial_answer_labels_uncovered_claims_and_cites_only_supporting_chunk() -> None:
    supported = make_result(
        "BA435 opens the customer account screen.",
        document_name="task-codes.pdf",
        screen_name="Customer Account Screen",
    )
    unrelated = make_result(
        "The settlement batch closes at end of day.", document_name="operations.pdf"
    )
    answer = await ask(
        (supported, unrelated),
        {
            "answer_text": (
                "BA435 opens the customer account screen. The knowledge base does not "
                "cover its approval workflow."
            ),
            "answer_type": "PARTIAL",
            "supported_chunk_ids": [str(supported.chunk.id)],
        },
    ).execute("What does BA435 do and what is its approval workflow?")

    assert answer.answer_type is AnswerType.PARTIAL
    assert "does not cover" in answer.answer_text
    assert [citation.document_name for citation in answer.citations] == ["task-codes.pdf"]


@pytest.mark.asyncio
async def test_ambiguous_answer_surfaces_candidates_without_citations() -> None:
    first = make_result(
        "The customer account screen handles account maintenance.",
        document_name="accounts.pdf",
        screen_name="Customer Account Screen",
    )
    second = make_result(
        "The account inquiry screen displays account details.",
        document_name="inquiry.pdf",
        screen_name="Account Inquiry Screen",
    )
    answer = await ask(
        (first, second),
        {
            "answer_text": "Your question could refer to more than one screen.",
            "answer_type": "AMBIGUOUS",
            "supported_chunk_ids": [],
        },
    ).execute("What does the account screen do?")

    assert answer.answer_type is AnswerType.AMBIGUOUS
    assert "Customer Account Screen" in answer.answer_text
    assert "Account Inquiry Screen" in answer.answer_text
    assert answer.citations == ()


@pytest.mark.asyncio
async def test_unknown_identifier_is_incorrect_premise_without_model_generation() -> None:
    retriever = Retriever(
        (make_result("BA435 opens the customer account screen.", document_name="manual.pdf"),)
    )
    llm = JsonLLM({"answer_text": "must not be used", "answer_type": "GROUNDED"})
    answer = await AskQuestion(
        retriever=retriever,
        llm=llm,
        llm_config=LLMConfig(provider="fake", model="test", endpoint="https://llm.test"),
        retrieval_config=RetrievalConfig(min_evidence_tokens=1),
    ).execute("Why does screen BA999 do X?")

    assert answer.answer_type is AnswerType.INCORRECT_PREMISE
    assert answer.citations == ()