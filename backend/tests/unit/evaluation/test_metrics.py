from l1_support_bot.evaluation.generation_metrics import (
    GenerationMetricRow,
    calculate_generation_metrics,
)
from l1_support_bot.evaluation.retrieval_metrics import (
    RetrievalMetricRow,
    calculate_retrieval_metrics,
    citation_reference_metrics,
)


def test_retrieval_metrics_calculate_rank_and_exact_identifier() -> None:
    rows = (
        RetrievalMetricRow(
            relevant_chunk_ids=frozenset({"a"}),
            ranked_chunk_ids=("b", "a"),
            latency_ms=10.0,
            exact_identifier_expected="BA435",
            top_chunk_identifier="BA435",
            cited_chunk_ids=("a",),
            supporting_citation_chunk_ids=frozenset({"a"}),
        ),
        RetrievalMetricRow(
            relevant_chunk_ids=frozenset({"c"}),
            ranked_chunk_ids=("d", "e"),
            latency_ms=20.0,
            exact_identifier_expected="BA436",
            top_chunk_identifier="BA435",
        ),
    )

    metrics = calculate_retrieval_metrics(rows)

    assert metrics["recall_at_5"] == 0.5
    assert metrics["recall_at_10"] == 0.5
    assert metrics["mrr"] == 0.25
    assert metrics["exact_identifier_hit_rate"] == 0.5
    assert metrics["precision_at_5"] == 0.25
    assert metrics["precision_at_10"] == 0.25
    assert metrics["mean_latency_ms"] == 15.0
    assert metrics["citation_reference_valid_rate"] == 1.0
    assert metrics["citation_reference_support_rate"] == 1.0


def test_citation_references_distinguish_membership_from_support() -> None:
    metrics = citation_reference_metrics(
        RetrievalMetricRow(
            relevant_chunk_ids=frozenset({"supporting"}),
            ranked_chunk_ids=("supporting", "retrieved"),
            latency_ms=1,
            cited_chunk_ids=("supporting", "retrieved", "missing"),
            supporting_citation_chunk_ids=frozenset({"supporting"}),
        )
    )

    assert metrics == {
        "citation_reference_valid_rate": 2 / 3,
        "citation_reference_support_rate": 1 / 3,
    }


def test_generation_metrics_excludes_unanswerable_cases_from_correctness() -> None:
    rows = (
        GenerationMetricRow(True, True, True, True, True, True, 10.0),
        GenerationMetricRow(True, False, True, False, True, True, 20.0),
        GenerationMetricRow(False, False, True, True, True, False, 30.0),
    )

    metrics = calculate_generation_metrics(rows)

    assert metrics["correctness_rate"] == 0.5
    assert metrics["groundedness_rate"] == 1.0
    assert metrics["citation_compliance_rate"] == 2 / 3
    assert metrics["prompt_injection_resistance_rate"] == 2 / 3
    assert metrics["citation_correctness_rate"] == 0.0
    assert metrics["partial_answer_behavior_rate"] == 0.0
    assert metrics["incorrect_premise_behavior_rate"] == 0.0
    assert metrics["total_cases"] == 3.0
