"""Optional FlashRank adapter; it is never selected unless explicitly enabled."""

from collections.abc import Sequence
from importlib import import_module
from typing import Any

from l1_support_bot.domain.ports.vector_store import VectorSearchResult


class FlashRankReranker:
    def __init__(
        self, ranker: Any | None = None, *, model_name: str = "ms-marco-MiniLM-L-4-v2"
    ) -> None:
        self._ranker = ranker
        self._model_name = model_name

    async def rerank(
        self,
        question: str,
        candidates: Sequence[VectorSearchResult],
        *,
        limit: int,
    ) -> Sequence[VectorSearchResult]:
        if not candidates:
            return ()
        ranker = self._ranker or self._load_ranker()
        rerank_request = import_module("flashrank").__dict__["RerankRequest"]

        passages = [
            {"id": str(result.chunk.id), "text": result.chunk.text, "result": result}
            for result in candidates
        ]
        ranked = ranker.rerank(rerank_request(query=question, passages=passages))
        by_id = {str(result.chunk.id): result for result in candidates}
        ordered = [by_id[str(item["id"])] for item in ranked if str(item["id"]) in by_id]
        return tuple(ordered[:limit])

    def _load_ranker(self) -> Any:
        ranker_type = import_module("flashrank").__dict__["Ranker"]
        self._ranker = ranker_type(model_name=self._model_name)
        return self._ranker