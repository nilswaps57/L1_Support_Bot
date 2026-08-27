"""Dense, lexical, exact-identifier, and metadata-filtered retrieval fusion."""

from collections.abc import Mapping, Sequence

from l1_support_bot.domain.models.configuration import EmbeddingConfig, RetrievalConfig
from l1_support_bot.domain.ports.embedding import EmbeddingPort
from l1_support_bot.domain.ports.retrieval import RetrieverPort
from l1_support_bot.domain.ports.vector_store import VectorSearchResult, VectorStorePort
from l1_support_bot.infrastructure.retrieval.identifier_extractor import extract_identifiers


class HybridRetriever(RetrieverPort):
    def __init__(
        self,
        *,
        vector_store: VectorStorePort,
        embedding: EmbeddingPort,
        embedding_config: EmbeddingConfig | None = None,
    ) -> None:
        self.vector_store = vector_store
        self.embedding = embedding
        self.embedding_config = embedding_config

    async def retrieve(
        self,
        question: str,
        *,
        limit: int = 5,
        filters: Mapping[str, str] | None = None,
        config: RetrievalConfig | None = None,
    ) -> Sequence[VectorSearchResult]:
        retrieval_config = config or RetrievalConfig(final_top_k=limit)
        if self.embedding_config is None:
            raise ValueError("Hybrid retrieval requires embedding configuration")
        query_vector = await self.embedding.embed_query(question, self.embedding_config)
        dense = await self.vector_store.search_dense(
            query_vector, limit=retrieval_config.top_k_candidates, filters=filters
        )
        terms = tuple(question.lower().split())
        sparse = await self.vector_store.search_sparse(
            terms, limit=retrieval_config.top_k_candidates, filters=filters
        )
        identifiers = extract_identifiers(question)
        exact: list[VectorSearchResult] = []
        for identifier in identifiers.all:
            key = "task_code" if identifier in identifiers.task_codes else (
                "error_code" if identifier in identifiers.error_codes else "jira_id"
            )
            exact.extend(
                result
                for result in await self.vector_store.search_dense(
                    query_vector,
                    limit=retrieval_config.top_k_candidates,
                    filters={key: identifier},
                )
                if getattr(result.chunk.metadata, key, None) == identifier
            )
        return self._fuse(dense, sparse, exact, retrieval_config)

    @staticmethod
    def _fuse(
        dense: Sequence[VectorSearchResult],
        sparse: Sequence[VectorSearchResult],
        exact: Sequence[VectorSearchResult],
        config: RetrievalConfig,
    ) -> Sequence[VectorSearchResult]:
        values: dict[object, tuple[VectorSearchResult, float]] = {}
        for source, results, weight in (
            ("dense", dense, config.dense_weight),
            ("sparse", sparse, config.sparse_weight),
            ("exact", exact, 1.0),
        ):
            for result in results:
                score = weight * result.score + (1.0 if source == "exact" else 0.0)
                current = values.get(result.chunk.id)
                values[result.chunk.id] = (
                    result,
                    (current[1] if current else 0.0) + score,
                )
        ranked = sorted(values.values(), key=lambda item: item[1], reverse=True)
        return tuple(
            VectorSearchResult(result.chunk, min(score, 1.0))
            for result, score in ranked[: config.final_top_k]
        )
