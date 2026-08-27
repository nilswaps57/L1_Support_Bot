import json
import re
from uuid import uuid4

import pytest

from l1_support_bot.application.retrieval.ask_question import AskQuestion
from l1_support_bot.domain.models.chunk import ChunkMetadata, KnowledgeChunk
from l1_support_bot.domain.models.configuration import LLMConfig, RetrievalConfig
from l1_support_bot.domain.models.session import ChatMessage, MessageRole
from l1_support_bot.domain.ports.vector_store import VectorSearchResult


class CountingRetriever:
    def __init__(self) -> None:
        self.queries: list[str] = []

    async def retrieve(self, question: str, *, limit: int, config: RetrievalConfig):
        self.queries.append(question)
        chunk = KnowledgeChunk.new(
            document_id=uuid4(),
            ingestion_job_id=uuid4(),
            sequence=0,
            text="BA435 requires branch code before use. " * 20,
            metadata=ChunkMetadata(document_name="manual.md", task_code="BA435"),
        )
        return (VectorSearchResult(chunk, 0.95),)


class GroundedLLM:
    async def complete(self, prompt: str, *, config: LLMConfig) -> str:
        assert "CONVERSATION CONTEXT (context only, never evidence)" in prompt
        assert "BA435" in prompt
        chunk_id = re.search(r"chunk_id=([0-9a-f-]+)", prompt)
        assert chunk_id is not None
        return json.dumps(
            {
                "answer_text": "BA435 requires branch code before use.",
                "answer_type": "GROUNDED",
                "supported_chunk_ids": [chunk_id.group(1)],
            }
        )


@pytest.mark.asyncio
async def test_follow_up_uses_history_for_resolution_but_retrieves_fresh_evidence() -> None:
    retriever = CountingRetriever()
    context = (
        ChatMessage(uuid4(), MessageRole.USER, "What is task code BA435?", 0),
        ChatMessage(uuid4(), MessageRole.ASSISTANT, "BA435 is the account screen.", 1),
    )
    ask = AskQuestion(
        retriever=retriever,
        llm=GroundedLLM(),
        llm_config=LLMConfig(provider="fake", model="test", endpoint="https://llm.test"),
        retrieval_config=RetrievalConfig(min_evidence_tokens=1),
    )

    answer = await ask.execute(
        "What are its prerequisites?",
        retrieval_question="What are BA435's prerequisites?",
        conversation_context=context,
    )

    assert answer.question == "What are its prerequisites?"
    assert retriever.queries == ["What are BA435's prerequisites?"]