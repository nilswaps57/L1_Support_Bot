"""Run dense-only versus local hybrid retrieval over a JSON evaluation fixture."""

from __future__ import annotations

import argparse
import asyncio
import json
import re
import time
from pathlib import Path
from statistics import mean
from typing import Any

from l1_support_bot.domain.models.configuration import EmbeddingConfig
from l1_support_bot.infrastructure.embedding.http_embedding import HttpEmbeddingAdapter

TOKEN = re.compile(r"[a-z0-9]+")
IDENTIFIER = re.compile(r"\b[A-Z]{2,5}\d{3,5}\b")


def cosine(left: list[float], right: list[float]) -> float:
    numerator = sum(a * b for a, b in zip(left, right, strict=True))
    left_norm = sum(value * value for value in left) ** 0.5
    right_norm = sum(value * value for value in right) ** 0.5
    return numerator / (left_norm * right_norm) if left_norm and right_norm else 0.0


def lexical_score(question: str, text: str) -> float:
    query_terms = set(TOKEN.findall(question.lower()))
    text_terms = set(TOKEN.findall(text.lower()))
    return len(query_terms & text_terms) / len(query_terms) if query_terms else 0.0


def rank(
    question: str,
    chunks: list[dict[str, Any]],
    vectors: list[list[float]],
    query_vector: list[float],
    *,
    hybrid: bool,
) -> list[str]:
    identifiers = set(IDENTIFIER.findall(question))
    scored: list[tuple[str, float]] = []
    for chunk, vector in zip(chunks, vectors, strict=True):
        dense = cosine(query_vector, vector)
        if not hybrid:
            score = dense
        else:
            lexical = lexical_score(question, str(chunk["text"]))
            exact = (
                1.0
                if identifiers and identifiers.intersection(IDENTIFIER.findall(str(chunk["text"])))
                else 0.0
            )
            score = 0.7 * dense + 0.3 * lexical + exact
        scored.append((str(chunk["id"]), score))
    return [chunk_id for chunk_id, _ in sorted(scored, key=lambda item: item[1], reverse=True)]


def metrics(rows: list[dict[str, Any]]) -> dict[str, float]:
    return {
        "recall_at_5": mean(row["recall_at_5"] for row in rows),
        "recall_at_10": mean(row["recall_at_10"] for row in rows),
        "mrr": mean(row["reciprocal_rank"] for row in rows),
        "exact_identifier_hit_rate": mean(row["exact_identifier_hit"] for row in rows),
        "query_latency_ms": mean(row["latency_ms"] for row in rows),
    }


async def evaluate(path: Path, endpoint: str, model: str, dimensions: int) -> dict[str, Any]:
    fixture = json.loads(path.read_text())
    chunks = list(fixture["chunks"])
    questions = list(fixture["questions"])
    config = EmbeddingConfig(
        provider="openai_compatible",
        model=model,
        model_version="live",
        endpoint=endpoint,
        dimensions=dimensions,
        index_compat_id=f"openai_compatible:{model}:live:{dimensions}",
    )
    adapter = HttpEmbeddingAdapter()
    started = time.perf_counter()
    vectors = await adapter.embed_batch([str(chunk["text"]) for chunk in chunks], config)
    batch_latency_ms = (time.perf_counter() - started) * 1000
    results: dict[str, Any] = {
        "fixture_id": fixture.get("fixture_id", path.stem),
        "model": model,
        "questions": len(questions),
        "chunks": len(chunks),
        "batch_latency_ms": batch_latency_ms,
        "vector_dimensions": len(vectors[0]) if vectors else 0,
        "modes": {},
    }
    for hybrid in (False, True):
        rows: list[dict[str, Any]] = []
        for question in questions:
            started = time.perf_counter()
            query_vector = await adapter.embed_query(str(question["question"]), config)
            ranked_ids = rank(
                str(question["question"]), chunks, vectors, query_vector, hybrid=hybrid
            )
            expected = set(question["relevant_chunk_ids"])
            rank_position = next(
                (
                    position
                    for position, chunk_id in enumerate(ranked_ids, 1)
                    if chunk_id in expected
                ),
                None,
            )
            top_chunk = next((chunk for chunk in chunks if str(chunk["id"]) == ranked_ids[0]), None)
            rows.append({
                "recall_at_5": bool(expected.intersection(ranked_ids[:5])),
                "recall_at_10": bool(expected.intersection(ranked_ids[:10])),
                "reciprocal_rank": 1 / rank_position if rank_position else 0.0,
                "exact_identifier_hit": bool(
                    ranked_ids
                    and top_chunk is not None
                    and question.get("identifier") == top_chunk.get("task_code")
                ),
                "latency_ms": (time.perf_counter() - started) * 1000,
            })
        results["modes"]["hybrid" if hybrid else "dense_only"] = metrics(rows)
    return results


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("fixture", type=Path)
    parser.add_argument("--endpoint", default="http://localhost:11434/v1")
    parser.add_argument("--model", default="nomic-embed-text")
    parser.add_argument("--dimensions", type=int, default=768)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    try:
        result = asyncio.run(evaluate(args.fixture, args.endpoint, args.model, args.dimensions))
    except Exception as error:
        print(json.dumps({"status": "blocked", "reason": str(error)}))
        return 2
    output = json.dumps({"status": "passed", **result}, indent=2)
    if args.output:
        args.output.write_text(output + "\n")
    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
