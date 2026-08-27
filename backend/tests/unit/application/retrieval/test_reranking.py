import json
import re
from uuid import uuid4

import pytest

from l1_support_bot.application.retrieval.ask_question import AskQuestion
from l1_support_bot.domain.models.chunk import ChunkMetadata, KnowledgeChunk
from l1_support_bot.domain.models.configuration import LLMConfig, RetrievalConfig
from l1_support_bot.domain.ports.vector_store import VectorSearchResult


def make_result(text: str) -> VectorSearchResult:
    return VectorSearchResult(
        KnowledgeChunk.new(
            document_id=uuid4(), ingestion_job_id=uuid4(), sequence=0,
            text=text, metadata=ChunkMetadata(document_name="manual.pdf"),
        ),
        0.9,
    )


class Retriever:
    def __init__(self, results: tuple[VectorSearchResult, ...]) -> None:
        self.results = results

    async def retrieve(self, question: str, *, limit: int, config: RetrievalConfig):
        return self.results


class Reranker:
    def __init__(self) -> None:
        self.calls = 0

    async def rerank(self, question, candidates, *, limit):
        self.calls += 1
        return tuple(reversed(candidates))[:limit]


class LLM:
    async def complete(self, prompt: str, *, config: LLMConfig) -> str:
        chunk_id = re.search(r"chunk_id=([0-9a-f-]+)", prompt)
        assert chunk_id is not None
        return json.dumps(
            {
                "answer_text": "The account screen is documented.",
                "answer_type": "GROUNDED",
                "supported_chunk_ids": [chunk_id.group(1)],
            }
        )


def build(reranker: Reranker, *, enabled: bool) -> AskQuestion:
    return AskQuestion(
        retriever=Retriever(
            (make_result("The account screen opens customer accounts."),
             make_result("The account screen displays account details."))
        ),
        llm=LLM(),
        llm_config=LLMConfig(provider="fake", model="test", endpoint="https://llm.test"),
        retrieval_config=RetrievalConfig(min_evidence_tokens=1, rerank_enabled=enabled),
        reranker=reranker,
    )


@pytest.mark.asyncio
async def test_reranking_is_disabled_by_default() -> None:
    reranker = Reranker()

    await build(reranker, enabled=False).execute("What is the account screen?")

    assert reranker.calls == 0


@pytest.mark.asyncio
async def test_reranking_is_used_only_when_explicitly_enabled() -> None:
    reranker = Reranker()

    await build(reranker, enabled=True).execute("What is the account screen?")

    assert reranker.calls == 1