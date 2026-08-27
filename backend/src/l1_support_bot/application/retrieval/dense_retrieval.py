"""Application orchestration for dense retrieval."""

from collections.abc import Mapping, Sequence

from l1_support_bot.domain.models.configuration import EmbeddingConfig
from l1_support_bot.domain.ports.embedding import EmbeddingPort
from l1_support_bot.domain.ports.vector_store import VectorSearchResult, VectorStorePort


class DenseRetrieval:
    def __init__(
        self,
        embedding: EmbeddingPort,
        vector_store: VectorStorePort,
        config: EmbeddingConfig,
    ) -> None:
        self.embedding = embedding
        self.vector_store = vector_store
        self.config = config

    async def retrieve(
        self, question: str, *, limit: int = 20, filters: Mapping[str, str] | None = None
    ) -> Sequence[VectorSearchResult]:
        vector = await self.embedding.embed_query(question, self.config)
        return await self.vector_store.search_dense(vector, limit=limit, filters=filters)
