from uuid import UUID, uuid4

import pytest

from l1_support_bot.application.retrieval.citation_builder import (
    CitationBuilder,
    CitationValidationError,
)
from l1_support_bot.domain.models.chunk import ChunkMetadata, KnowledgeChunk
from l1_support_bot.domain.ports.vector_store import VectorSearchResult


def make_result(
    *,
    document_id: UUID | None = None,
    document_name: str = "FLEXCUBE Manual",
    page_number: int | None = 142,
) -> VectorSearchResult:
    resolved_document_id = document_id or uuid4()
    chunk = KnowledgeChunk.new(
        document_id=resolved_document_id,
        ingestion_job_id=uuid4(),
        sequence=3,
        text="BA435 opens the customer account screen.",
        metadata=ChunkMetadata(
            document_name=document_name,
            page_number=page_number,
            section="Chapter 5 > Task Codes > BA435",
            task_code="BA435",
            screen_name="Customer Account Screen",
            error_code="ORA-00942",
            jira_id="JIRA-1234",
            source_type="flexcube_manual",
        ),
    )
    return VectorSearchResult(chunk, 0.92)


def test_builds_only_materially_supported_retrieved_chunk_and_preserves_metadata() -> None:
    supporting = make_result()
    unrelated = make_result(document_name="Unrelated manual", page_number=9)

    citations = CitationBuilder().build(
        (supporting, unrelated),
        supported_chunk_ids=(supporting.chunk.id,),
        available_document_ids={supporting.chunk.document_id, unrelated.chunk.document_id},
    )

    assert len(citations) == 1
    citation = citations[0]
    assert citation.chunk_id == supporting.chunk.id
    assert citation.document_id == supporting.chunk.document_id
    assert citation.document_name == "FLEXCUBE Manual"
    assert citation.page_number == 142
    assert citation.section == "Chapter 5 > Task Codes > BA435"
    assert citation.task_code == "BA435"
    assert citation.screen_name == "Customer Account Screen"
    assert citation.error_code == "ORA-00942"
    assert citation.jira_id == "JIRA-1234"
    assert citation.relevance_score == 0.92


def test_missing_page_metadata_is_preserved_as_missing() -> None:
    result = make_result(page_number=None)

    citation = CitationBuilder().build(
        (result,),
        supported_chunk_ids=(result.chunk.id,),
        available_document_ids={result.chunk.document_id},
    )[0]

    assert citation.page_number is None


def test_rejects_fabricated_chunk_identity() -> None:
    result = make_result()

    with pytest.raises(CitationValidationError, match="was not retrieved"):
        CitationBuilder().build(
            (result,),
            supported_chunk_ids=(uuid4(),),
            available_document_ids={result.chunk.document_id},
        )


def test_rejects_deleted_or_unavailable_document() -> None:
    result = make_result()

    with pytest.raises(CitationValidationError, match="not available"):
        CitationBuilder().build(
            (result,),
            supported_chunk_ids=(result.chunk.id,),
            available_document_ids=set(),
        )


def test_requires_explicit_supported_references() -> None:
    result = make_result()

    with pytest.raises(CitationValidationError, match="supported chunk"):
        CitationBuilder().build(
            (result,),
            supported_chunk_ids=(),
            available_document_ids={result.chunk.document_id},
        )
