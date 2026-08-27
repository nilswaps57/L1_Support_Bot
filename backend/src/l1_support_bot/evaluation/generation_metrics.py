"""Deterministic aggregation for human-reviewed generation outcomes."""

from __future__ import annotations

from dataclasses import dataclass
from statistics import mean


@dataclass(frozen=True, slots=True)
class GenerationMetricRow:
    answerable: bool
    correctness: bool
    groundedness: bool
    citation_compliant: bool
    insufficient_information_behavior: bool
    prompt_injection_resistant: bool
    latency_ms: float
    citation_correctness: bool | None = None
    citation_completeness: bool | None = None
    partial_answer_behavior: bool | None = None
    ambiguity_behavior: bool | None = None
    unsupported_claims_absent: bool | None = None
    incorrect_premise_behavior: bool | None = None


def _observed_rate(rows: tuple[GenerationMetricRow, ...], attribute: str) -> float:
    values = tuple(
        value
        for value in (getattr(row, attribute) for row in rows)
        if value is not None
    )
    return mean(values) if values else 0.0


def calculate_generation_metrics(rows: tuple[GenerationMetricRow, ...]) -> dict[str, float]:
    if not rows:
        raise ValueError("At least one generation metric row is required")
    answerable_rows = tuple(row for row in rows if row.answerable)
    return {
        "correctness_rate": mean(row.correctness for row in answerable_rows)
        if answerable_rows else 0.0,
        "groundedness_rate": mean(row.groundedness for row in rows),
        "citation_compliance_rate": mean(row.citation_compliant for row in rows),
        "citation_correctness_rate": _observed_rate(rows, "citation_correctness"),
        "citation_completeness_rate": _observed_rate(rows, "citation_completeness"),
        "insufficient_information_behavior_rate": mean(
            row.insufficient_information_behavior for row in rows
        ),
        "partial_answer_behavior_rate": _observed_rate(rows, "partial_answer_behavior"),
        "ambiguity_behavior_rate": _observed_rate(rows, "ambiguity_behavior"),
        "unsupported_claims_absent_rate": _observed_rate(rows, "unsupported_claims_absent"),
        "incorrect_premise_behavior_rate": _observed_rate(
            rows, "incorrect_premise_behavior"
        ),
        "prompt_injection_resistance_rate": mean(
            row.prompt_injection_resistant for row in rows
        ),
        "mean_latency_ms": mean(row.latency_ms for row in rows),
        "answerable_cases": float(len(answerable_rows)),
        "total_cases": float(len(rows)),
    }
