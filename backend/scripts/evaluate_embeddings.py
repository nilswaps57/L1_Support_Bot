"""Measure embedding candidates on an externally supplied FLEXCUBE fixture."""

from __future__ import annotations

import argparse
import asyncio
import json
import time
from pathlib import Path
from statistics import mean
from typing import Any

from l1_support_bot.domain.models.configuration import EmbeddingConfig
from l1_support_bot.infrastructure.embedding.http_embedding import HttpEmbeddingAdapter


async def evaluate(candidate: dict[str, Any], fixture: dict[str, Any]) -> dict[str, Any]:
    texts = [str(item["text"]) for item in fixture["chunks"]]
    config = EmbeddingConfig(
        provider=str(candidate["provider"]),
        model=str(candidate["model"]),
        model_version=str(candidate.get("model_version", "unknown")),
        endpoint=str(candidate["endpoint"]),
        dimensions=int(candidate["dimensions"]),
        index_compat_id=(
            f"{candidate['provider']}:{candidate['model']}:{candidate.get('model_version', 'unknown')}:{candidate['dimensions']}"
        ),
    )
    adapter = HttpEmbeddingAdapter()
    started = time.perf_counter()
    vectors = await adapter.embed_batch(texts, config)
    latency_ms = (time.perf_counter() - started) * 1000
    rows: list[dict[str, Any]] = []
    for question in fixture["questions"]:
        query_started = time.perf_counter()
        query_vector = await adapter.embed_query(str(question["question"]), config)
        scored = sorted(
            ((index, _cosine(query_vector, vector)) for index, vector in enumerate(vectors)),
            key=lambda item: item[1],
            reverse=True,
        )
        expected = set(question["relevant_chunk_ids"])
        ranked_ids = [fixture["chunks"][index]["id"] for index, _ in scored]
        rank = next((position for position, item in enumerate(ranked_ids, 1) if item in expected), None)
        top_chunk = next((chunk for chunk in fixture["chunks"] if chunk["id"] == ranked_ids[0]), None)
        rows.append({
            "recall_at_5": bool(expected.intersection(ranked_ids[:5])),
            "recall_at_10": bool(expected.intersection(ranked_ids[:10])),
            "reciprocal_rank": 1 / rank if rank else 0.0,
            "exact_identifier_hit": bool(
                top_chunk is not None
                and question.get("identifier") == top_chunk.get("task_code")
            ),
            "latency_ms": (time.perf_counter() - query_started) * 1000,
        })
    return {
        "candidate": candidate,
        "questions": len(rows),
        "recall_at_5": mean(row["recall_at_5"] for row in rows),
        "recall_at_10": mean(row["recall_at_10"] for row in rows),
        "mrr": mean(row["reciprocal_rank"] for row in rows),
        "exact_identifier_hit_rate": mean(row["exact_identifier_hit"] for row in rows),
        "batch_latency_ms": latency_ms,
        "query_latency_ms": mean(row["latency_ms"] for row in rows),
        "vector_dimensions": len(vectors[0]) if vectors else 0,
        "estimated_vector_bytes": len(vectors) * config.dimensions * 4,
        "licensing": candidate.get("licensing", "not supplied"),
        "deployment": candidate.get("deployment", "not supplied"),
    }


def _cosine(left: Any, right: Any) -> float:
    numerator = sum(a * b for a, b in zip(left, right, strict=True))
    left_norm = sum(value * value for value in left) ** 0.5
    right_norm = sum(value * value for value in right) ** 0.5
    return numerator / (left_norm * right_norm) if left_norm and right_norm else 0.0


async def run(fixture_path: Path, candidates_path: Path) -> list[dict[str, Any]]:
    fixture = json.loads(fixture_path.read_text())
    candidates = json.loads(candidates_path.read_text())
    if not fixture.get("chunks") or not fixture.get("questions"):
        raise ValueError("Fixture must contain chunks and questions")
    return [await evaluate(candidate, fixture) for candidate in candidates]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("fixture", type=Path)
    parser.add_argument("candidates", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    try:
        results = asyncio.run(run(args.fixture, args.candidates))
    except Exception as error:
        print(json.dumps({"status": "blocked", "reason": str(error)}))
        return 2
    output = json.dumps({"status": "passed", "results": results}, indent=2)
    if args.output:
        args.output.write_text(output + "\n")
    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
