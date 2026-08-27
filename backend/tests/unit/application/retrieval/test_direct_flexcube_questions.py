import pytest

from l1_support_bot.domain.models.chunk import ChunkMetadata, KnowledgeChunk
from l1_support_bot.infrastructure.retrieval.identifier_extractor import extract_identifiers
from l1_support_bot.infrastructure.retrieval.lexical_retriever import LexicalRetriever


def test_extracts_task_error_and_jira_identifiers() -> None:
    identifiers = extract_identifiers("How do I use BA435 for ORA-00942? See JIRA-1234")

    assert "BA435" in identifiers.task_codes
    assert "ORA-00942" in identifiers.error_codes
    assert "JIRA-1234" in identifiers.jira_ids


@pytest.mark.asyncio
async def test_lexical_retrieval_matches_documented_identifiers() -> None:
    chunk = KnowledgeChunk.new(
        document_id=__import__("uuid").uuid4(), ingestion_job_id=__import__("uuid").uuid4(),
        sequence=0, text="BA435 opens the customer account screen.",
        metadata=ChunkMetadata(document_name="manual", task_code="BA435"),
    )
    results = await LexicalRetriever((chunk,)).retrieve("BA435", limit=1)

    assert results[0].chunk.id == chunk.id
