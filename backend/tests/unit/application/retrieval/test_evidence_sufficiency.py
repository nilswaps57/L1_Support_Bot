from uuid import uuid4

from l1_support_bot.application.retrieval.evidence_sufficiency import (
    EvidenceStatus,
    EvidenceSufficiencyPolicy,
)
from l1_support_bot.domain.models.chunk import ChunkMetadata, KnowledgeChunk
from l1_support_bot.domain.models.configuration import RetrievalConfig
from l1_support_bot.domain.ports.vector_store import VectorSearchResult


def make_result(text: str, score: float = 0.9, task_code: str | None = None) -> VectorSearchResult:
    chunk = KnowledgeChunk.new(
        document_id=uuid4(),
        ingestion_job_id=uuid4(),
        sequence=0,
        text=text,
        metadata=ChunkMetadata(document_name="manual.md", task_code=task_code),
    )
    return VectorSearchResult(chunk, score)


def policy(**kwargs: object) -> EvidenceSufficiencyPolicy:
    return EvidenceSufficiencyPolicy(RetrievalConfig(**kwargs))


def test_no_results_are_insufficient() -> None:
    assessment = policy().evaluate("What is BA435?", ())

    assert assessment.status is EvidenceStatus.INSUFFICIENT
    assert assessment.results == ()


def test_results_below_score_threshold_are_insufficient() -> None:
    result = make_result("BA435 opens the customer account screen.", score=0.39, task_code="BA435")

    assessment = policy(similarity_threshold=0.4).evaluate(
        "What is the customer account screen?", (result,)
    )

    assert assessment.status is EvidenceStatus.INSUFFICIENT


def test_low_token_evidence_is_insufficient() -> None:
    result = make_result("The screen.", score=0.9)

    assessment = policy(min_evidence_tokens=10).evaluate("What is the screen?", (result,))

    assert assessment.status is EvidenceStatus.INSUFFICIENT


def test_exact_identifier_bypasses_score_and_token_thresholds() -> None:
    result = make_result("BA435 opens the customer account screen.", score=0.1, task_code="BA435")

    assessment = policy(similarity_threshold=0.4, min_evidence_tokens=100).evaluate(
        "What is task code BA435?", (result,)
    )

    assert assessment.status is EvidenceStatus.SUFFICIENT
    assert assessment.results == (result,)


def test_high_score_irrelevant_evidence_is_insufficient() -> None:
    result = make_result("The settlement batch is closed at end of day.", score=0.95)

    assessment = policy().evaluate("What is the customer account screen?", (result,))

    assert assessment.status is EvidenceStatus.INSUFFICIENT


def test_relevant_partial_evidence_is_available_for_generation() -> None:
    result = make_result(
        "BA435 opens the customer account screen. The indexed manual does not "
        "describe its approval workflow.",
        score=0.9,
        task_code="BA435",
    )

    assessment = policy(min_evidence_tokens=10).evaluate(
        "What does BA435 do and what is its approval workflow?", (result,)
    )

    assert assessment.status is EvidenceStatus.SUFFICIENT
    assert assessment.results == (result,)
