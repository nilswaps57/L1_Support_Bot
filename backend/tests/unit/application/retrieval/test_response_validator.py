from uuid import uuid4

import pytest

from l1_support_bot.application.retrieval.citation_builder import CitationValidationError
from l1_support_bot.application.retrieval.response_validator import ResponseValidator
from l1_support_bot.domain.models.answer import Answer, AnswerType
from l1_support_bot.domain.models.chunk import ChunkMetadata, KnowledgeChunk
from l1_support_bot.domain.models.citation import Citation
from l1_support_bot.domain.ports.vector_store import VectorSearchResult


def make_result() -> VectorSearchResult:
    document_id = uuid4()
    chunk = KnowledgeChunk.new(
        document_id=document_id,
        ingestion_job_id=uuid4(),
        sequence=0,
        text="BA435 opens the customer account screen.",
        metadata=ChunkMetadata(document_name="FLEXCUBE Manual", task_code="BA435"),
    )
    return VectorSearchResult(chunk, 0.95)


def make_citation(result: VectorSearchResult) -> Citation:
    return Citation(
        chunk_id=result.chunk.id,
        document_id=result.chunk.document_id,
        document_name=result.chunk.metadata.document_name,
        task_code=result.chunk.metadata.task_code,
    )


def test_accepts_citations_that_belong_to_current_retrieval_and_available_sources() -> None:
    result = make_result()
    answer = Answer(
        question="What is BA435?",
        answer_text="BA435 opens the customer account screen.",
        answer_type=AnswerType.GROUNDED,
        citations=(make_citation(result),),
    )

    validated = ResponseValidator().validate(
        answer,
        retrieved=(result,),
        available_document_ids={result.chunk.document_id},
    )

    assert validated is answer


def test_rejects_citation_for_chunk_not_in_current_retrieval() -> None:
    result = make_result()
    answer = Answer(
        question="What is BA435?",
        answer_text="BA435 opens the customer account screen.",
        answer_type=AnswerType.GROUNDED,
        citations=(
            Citation(
                chunk_id=uuid4(),
                document_id=result.chunk.document_id,
                document_name="FLEXCUBE Manual",
            ),
        ),
    )

    with pytest.raises(CitationValidationError, match="was not retrieved"):
        ResponseValidator().validate(answer, retrieved=(result,))


def test_rejects_citation_from_deleted_or_unavailable_document() -> None:
    result = make_result()
    answer = Answer(
        question="What is BA435?",
        answer_text="BA435 opens the customer account screen.",
        answer_type=AnswerType.GROUNDED,
        citations=(make_citation(result),),
    )

    with pytest.raises(CitationValidationError, match="not available"):
        ResponseValidator().validate(answer, retrieved=(result,), available_document_ids=set())


def test_insufficient_answer_has_no_citations() -> None:
    answer = Answer.insufficient(
        "The available knowledge sources do not contain sufficient information."
    )

    validated = ResponseValidator().validate(answer, retrieved=())

    assert validated.answer_type is AnswerType.INSUFFICIENT
    assert validated.citations == ()


def test_rejects_answer_without_citation_coverage() -> None:
    with pytest.raises(ValueError, match="require supporting citations"):
        Answer(
            question="What is BA435?",
            answer_text="BA435 opens a screen.",
            answer_type=AnswerType.GROUNDED,
        )
