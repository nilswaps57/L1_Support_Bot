"""Deterministic retrieval metric calculation for reviewed evaluation runs."""

from __future__ import annotations

from dataclasses import dataclass
from statistics import mean


@dataclass(frozen=True, slots=True)
class RetrievalMetricRow:
    relevant_chunk_ids: frozenset[str]
    ranked_chunk_ids: tuple[str, ...]
    latency_ms: float
    exact_identifier_expected: str | None = None
    top_chunk_identifier: str | None = None
    cited_chunk_ids: tuple[str, ...] = ()
    supporting_citation_chunk_ids: frozenset[str] = frozenset()


def reciprocal_rank(row: RetrievalMetricRow) -> float:
    rank = next(
        (position for position, chunk_id in enumerate(row.ranked_chunk_ids, 1)
         if chunk_id in row.relevant_chunk_ids),
        None,
    )
    return 1.0 / rank if rank is not None else 0.0


def _precision_at(row: RetrievalMetricRow, limit: int) -> float:
    ranked = row.ranked_chunk_ids[:limit]
    if not ranked:
        return 0.0
    return len(row.relevant_chunk_ids.intersection(ranked)) / len(ranked)


def citation_reference_metrics(row: RetrievalMetricRow) -> dict[str, float]:
    """Measure citation references without treating retrieval as proof of support."""
    cited = tuple(dict.fromkeys(row.cited_chunk_ids))
    if not cited:
        return {
            "citation_reference_valid_rate": 1.0,
            "citation_reference_support_rate": 1.0,
        }
    retrieved = set(row.ranked_chunk_ids)
    return {
        "citation_reference_valid_rate": sum(chunk_id in retrieved for chunk_id in cited)
        / len(cited),
        "citation_reference_support_rate": sum(
            chunk_id in row.supporting_citation_chunk_ids for chunk_id in cited
        )
        / len(cited),
    }


def _eligible_rate(values: tuple[bool, ...]) -> float:
    return mean(values) if values else 0.0


def calculate_retrieval_metrics(rows: tuple[RetrievalMetricRow, ...]) -> dict[str, float]:
    if not rows:
        raise ValueError("At least one retrieval metric row is required")
    return {
        "recall_at_5": mean(
            bool(row.relevant_chunk_ids.intersection(row.ranked_chunk_ids[:5])) for row in rows
        ),
        "recall_at_10": mean(
            bool(row.relevant_chunk_ids.intersection(row.ranked_chunk_ids[:10])) for row in rows
        ),
        "precision_at_5": mean(_precision_at(row, 5) for row in rows),
        "precision_at_10": mean(_precision_at(row, 10) for row in rows),
        "mrr": mean(reciprocal_rank(row) for row in rows),
        "exact_identifier_hit_rate": _eligible_rate(tuple(
            row.exact_identifier_expected == row.top_chunk_identifier
            for row in rows
            if row.exact_identifier_expected is not None
        )),
        "mean_latency_ms": mean(row.latency_ms for row in rows),
        "citation_reference_valid_rate": mean(
            citation_reference_metrics(row)["citation_reference_valid_rate"] for row in rows
        ),
        "citation_reference_support_rate": mean(
            citation_reference_metrics(row)["citation_reference_support_rate"] for row in rows
        ),
    }
