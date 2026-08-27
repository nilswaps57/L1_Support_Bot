"""Deterministic lexical candidate generation for local and test use."""

import re
from collections.abc import Sequence
from importlib import import_module
from typing import Any

from l1_support_bot.domain.models.chunk import KnowledgeChunk
from l1_support_bot.domain.ports.vector_store import VectorSearchResult

BM25Okapi: Any = import_module("rank_bm25").BM25Okapi


class LexicalRetriever:
    def __init__(self, chunks: Sequence[KnowledgeChunk] = ()) -> None:
        self.chunks = tuple(chunks)
        self._index = (
            BM25Okapi([_terms(chunk.text) for chunk in self.chunks])
            if self.chunks
            else None
        )

    async def retrieve(
        self, question: str, *, limit: int, filters: dict[str, str] | None = None
    ) -> Sequence[VectorSearchResult]:
        query_terms = set(_terms(question))
        scored: list[VectorSearchResult] = []
        scores = self._index.get_scores(tuple(query_terms)) if self._index else ()
        for chunk, raw_score in zip(self.chunks, scores, strict=True):
            if filters and any(
                getattr(chunk.metadata, key, None) != value
                for key, value in filters.items()
            ):
                continue
            terms = set(_terms(chunk.text))
            score = (
                float(raw_score)
                if raw_score
                else len(query_terms.intersection(terms)) / max(len(query_terms), 1)
            )
            if score:
                scored.append(VectorSearchResult(chunk, min(score, 1.0)))
        return tuple(sorted(scored, key=lambda item: item.score, reverse=True)[:limit])


def _terms(text: str) -> tuple[str, ...]:
    return tuple(re.findall(r"[a-z0-9][a-z0-9_-]*", text.lower()))
