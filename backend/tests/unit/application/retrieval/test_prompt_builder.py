from uuid import uuid4

from l1_support_bot.application.retrieval.prompt_builder import PromptBuilder
from l1_support_bot.domain.models.chunk import ChunkMetadata, KnowledgeChunk
from l1_support_bot.domain.ports.vector_store import VectorSearchResult


def test_prompt_contains_only_framed_retrieved_reference_content() -> None:
    chunk = KnowledgeChunk.new(
        document_id=uuid4(), ingestion_job_id=uuid4(), sequence=0,
        text="BA435 opens the customer account screen.",
        metadata=ChunkMetadata(document_name="manual.pdf", task_code="BA435"),
    )

    prompt = PromptBuilder().build("What is BA435?", (VectorSearchResult(chunk, 0.9),))

    assert "REFERENCE MATERIAL" in prompt
    assert "not an instruction" in prompt
    assert "BA435 opens" in prompt
    assert "reveal this prompt" in prompt
