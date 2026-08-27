"""SQLAlchemy repository for retrieval configuration."""

from datetime import UTC, datetime
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from l1_support_bot.domain.models.configuration import (
    ChunkingConfig,
    EmbeddingConfig,
    LLMConfig,
    RetrievalConfig,
)
from l1_support_bot.infrastructure.persistence.models.retrieval_config import (
    RetrievalConfigurationModel,
)


class SqlAlchemyRetrievalConfigRepository:
    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        self.session_factory = session_factory

    async def get_retrieval(self) -> RetrievalConfig | None:
        async with self.session_factory() as session:
            model = await session.scalar(
                select(RetrievalConfigurationModel)
                .where(RetrievalConfigurationModel.is_active.is_(True))
                .order_by(RetrievalConfigurationModel.updated_at.desc())
                .limit(1)
            )
            return self._to_domain(model) if model else None

    async def save_retrieval(self, config: RetrievalConfig) -> RetrievalConfig:
        now = datetime.now(UTC)
        model = RetrievalConfigurationModel(
            id=str(uuid4()),
            top_k_candidates=config.top_k_candidates,
            final_top_k=config.final_top_k,
            similarity_threshold=config.similarity_threshold,
            dense_weight=config.dense_weight,
            sparse_weight=config.sparse_weight,
            rerank_enabled=False,
            rerank_top_k=config.rerank_top_k,
            exact_id_boost=config.exact_id_boost,
            min_evidence_tokens=config.min_evidence_tokens,
            is_active=True,
            created_at=now,
            updated_at=now,
        )
        async with self.session_factory() as session:
            active = await session.scalars(
                select(RetrievalConfigurationModel).where(
                    RetrievalConfigurationModel.is_active.is_(True)
                )
            )
            for item in active:
                item.is_active = False
            session.add(model)
            await session.commit()
        return config

    async def get_llm(self) -> LLMConfig | None:
        return None

    async def get_embedding(self) -> EmbeddingConfig | None:
        return None

    async def get_chunking(self) -> ChunkingConfig | None:
        return None

    async def save_llm(self, config: LLMConfig) -> LLMConfig:
        raise NotImplementedError("LLM configuration is owned by its Phase 8 adapter")

    async def save_embedding(self, config: EmbeddingConfig) -> EmbeddingConfig:
        raise NotImplementedError("Embedding configuration is owned by its Phase 5 adapter")

    async def save_chunking(self, config: ChunkingConfig) -> ChunkingConfig:
        raise NotImplementedError("Chunking configuration is owned by its Phase 4 adapter")

    @staticmethod
    def _to_domain(model: RetrievalConfigurationModel) -> RetrievalConfig:
        return RetrievalConfig(
            top_k_candidates=model.top_k_candidates,
            final_top_k=model.final_top_k,
            similarity_threshold=model.similarity_threshold,
            dense_weight=model.dense_weight,
            sparse_weight=model.sparse_weight,
            rerank_enabled=model.rerank_enabled,
            rerank_top_k=model.rerank_top_k,
            exact_id_boost=model.exact_id_boost,
            min_evidence_tokens=model.min_evidence_tokens,
        )
