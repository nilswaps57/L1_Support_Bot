"""SQLAlchemy repository for active AI and RAG configuration snapshots."""

from datetime import UTC, datetime
from typing import Any, cast
from uuid import uuid4

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from l1_support_bot.domain.models.configuration import (
    ChunkingConfig,
    ConfigurationSnapshot,
    EmbeddingConfig,
    LLMConfig,
    RetrievalConfig,
)
from l1_support_bot.infrastructure.persistence.models.chunks import KnowledgeChunkModel
from l1_support_bot.infrastructure.persistence.models.configuration import (
    EmbeddingConfigurationModel,
)
from l1_support_bot.infrastructure.persistence.models.documents import DocumentModel
from l1_support_bot.infrastructure.persistence.models.llm_config import (
    ChunkingConfigurationModel,
    LLMConfigurationModel,
)
from l1_support_bot.infrastructure.persistence.models.retrieval_config import (
    RetrievalConfigurationModel,
)


class SqlAlchemyRetrievalConfigRepository:
    """The historical class name is retained for retrieval API compatibility."""

    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        self.session_factory = session_factory

    async def get_llm(self) -> LLMConfig | None:
        async with self.session_factory() as session:
            model = await self._active(session, LLMConfigurationModel)
            return self._to_llm(model) if model else None

    async def get_embedding(self) -> EmbeddingConfig | None:
        async with self.session_factory() as session:
            model = await self._active(session, EmbeddingConfigurationModel)
            return self._to_embedding(model) if model else None

    async def get_retrieval(self) -> RetrievalConfig | None:
        async with self.session_factory() as session:
            model = await self._active(session, RetrievalConfigurationModel)
            return self._to_retrieval(model) if model else None

    async def get_chunking(self) -> ChunkingConfig | None:
        async with self.session_factory() as session:
            model = await self._active(session, ChunkingConfigurationModel)
            return self._to_chunking(model) if model else None

    async def save_llm(self, config: LLMConfig) -> LLMConfig:
        return cast(LLMConfig, await self._save_single(config, "llm"))

    async def save_embedding(self, config: EmbeddingConfig) -> EmbeddingConfig:
        return cast(EmbeddingConfig, await self._save_single(config, "embedding"))

    async def save_retrieval(self, config: RetrievalConfig) -> RetrievalConfig:
        return cast(RetrievalConfig, await self._save_single(config, "retrieval"))

    async def save_chunking(self, config: ChunkingConfig) -> ChunkingConfig:
        return cast(ChunkingConfig, await self._save_single(config, "chunking"))

    async def count_indexed_documents(self) -> int:
        async with self.session_factory() as session:
            statement = (
                select(func.count(func.distinct(KnowledgeChunkModel.document_id)))
                .join(DocumentModel, DocumentModel.id == KnowledgeChunkModel.document_id)
                .where(DocumentModel.status.in_(("COMPLETED", "COMPLETED_WITH_WARNING")))
            )
            return int(await session.scalar(statement) or 0)

    async def save_all(self, configuration: object) -> None:
        if not isinstance(configuration, ConfigurationSnapshot):
            raise TypeError("Expected a complete configuration snapshot")
        now = datetime.now(UTC)
        async with self.session_factory() as session:
            async with session.begin():
                model_types: tuple[Any, ...] = (
                    LLMConfigurationModel,
                    EmbeddingConfigurationModel,
                    RetrievalConfigurationModel,
                    ChunkingConfigurationModel,
                )
                for model_type in model_types:
                    active = await session.scalars(
                        select(model_type).where(model_type.is_active.is_(True))
                    )
                    for item in active:
                        item.is_active = False
                session.add(self._llm_model(configuration.llm, now))
                session.add(self._embedding_model(configuration.embedding, now))
                session.add(self._retrieval_model(configuration.retrieval, now))
                session.add(self._chunking_model(configuration.chunking, now))

    async def _save_single(self, config: Any, category: str) -> Any:
        now = datetime.now(UTC)
        model_types: dict[str, Any] = {
            "llm": LLMConfigurationModel,
            "embedding": EmbeddingConfigurationModel,
            "retrieval": RetrievalConfigurationModel,
            "chunking": ChunkingConfigurationModel,
        }
        model_type = model_types[category]
        async with self.session_factory() as session:
            async with session.begin():
                active = await session.scalars(
                    select(model_type).where(model_type.is_active.is_(True))
                )
                for item in active:
                    item.is_active = False
                builders: dict[str, Any] = {
                    "llm": self._llm_model,
                    "embedding": self._embedding_model,
                    "retrieval": self._retrieval_model,
                    "chunking": self._chunking_model,
                }
                model = builders[category](config, now)
                session.add(model)
        return config

    @staticmethod
    async def _active(session: AsyncSession, model_type: Any) -> Any:
        return await session.scalar(
            select(model_type)
            .where(model_type.is_active.is_(True))
            .order_by(model_type.updated_at.desc())
            .limit(1)
        )

    @staticmethod
    def _llm_model(config: LLMConfig, now: datetime) -> LLMConfigurationModel:
        return LLMConfigurationModel(
            id=str(uuid4()),
            provider=config.provider,
            model=config.model,
            endpoint=config.endpoint,
            temperature=config.temperature,
            max_tokens=config.max_tokens,
            context_window=config.context_window,
            timeout_seconds=config.timeout_seconds,
            max_retries=config.max_retries,
            is_active=True,
            label=config.label,
            created_at=now,
            updated_at=now,
        )

    @staticmethod
    def _embedding_model(config: EmbeddingConfig, now: datetime) -> EmbeddingConfigurationModel:
        return EmbeddingConfigurationModel(
            id=str(uuid4()),
            provider=config.provider,
            model=config.model,
            model_version=config.model_version,
            endpoint=config.endpoint,
            dimensions=config.dimensions,
            distance_method=config.distance_method,
            index_compat_id=config.index_compat_id,
            batch_size=config.batch_size,
            timeout_seconds=config.timeout_seconds,
            is_active=True,
            label=config.label,
            created_at=now,
            updated_at=now,
        )

    @staticmethod
    def _retrieval_model(config: RetrievalConfig, now: datetime) -> RetrievalConfigurationModel:
        return RetrievalConfigurationModel(
            id=str(uuid4()),
            top_k_candidates=config.top_k_candidates,
            final_top_k=config.final_top_k,
            similarity_threshold=config.similarity_threshold,
            dense_weight=config.dense_weight,
            sparse_weight=config.sparse_weight,
            rerank_enabled=config.rerank_enabled,
            rerank_top_k=config.rerank_top_k,
            exact_id_boost=config.exact_id_boost,
            min_evidence_tokens=config.min_evidence_tokens,
            is_active=True,
            created_at=now,
            updated_at=now,
        )

    @staticmethod
    def _chunking_model(config: ChunkingConfig, now: datetime) -> ChunkingConfigurationModel:
        return ChunkingConfigurationModel(
            id=str(uuid4()),
            strategy=config.strategy,
            target_chunk_tokens=config.target_chunk_tokens,
            min_chunk_tokens=config.min_chunk_tokens,
            max_chunk_tokens=config.max_chunk_tokens,
            overlap_tokens=config.overlap_tokens,
            table_as_unit=config.table_as_unit,
            procedure_grouping=config.procedure_grouping,
            is_active=True,
            created_at=now,
            updated_at=now,
        )

    @staticmethod
    def _to_llm(model: LLMConfigurationModel) -> LLMConfig:
        return LLMConfig(
            config_id=model.id,
            provider=model.provider,
            model=model.model,
            endpoint=model.endpoint,
            temperature=model.temperature,
            max_tokens=model.max_tokens,
            context_window=model.context_window,
            timeout_seconds=model.timeout_seconds,
            max_retries=model.max_retries,
            is_active=model.is_active,
            label=model.label,
        )

    @staticmethod
    def _to_embedding(model: EmbeddingConfigurationModel) -> EmbeddingConfig:
        return EmbeddingConfig(
            config_id=model.id,
            provider=model.provider,
            model=model.model,
            model_version=model.model_version,
            endpoint=model.endpoint,
            dimensions=model.dimensions,
            distance_method=model.distance_method,
            index_compat_id=model.index_compat_id,
            batch_size=model.batch_size,
            timeout_seconds=model.timeout_seconds,
            is_active=model.is_active,
            label=model.label,
        )

    @staticmethod
    def _to_retrieval(model: RetrievalConfigurationModel) -> RetrievalConfig:
        return RetrievalConfig(
            config_id=model.id,
            top_k_candidates=model.top_k_candidates,
            final_top_k=model.final_top_k,
            similarity_threshold=model.similarity_threshold,
            dense_weight=model.dense_weight,
            sparse_weight=model.sparse_weight,
            rerank_enabled=model.rerank_enabled,
            rerank_top_k=model.rerank_top_k,
            exact_id_boost=model.exact_id_boost,
            min_evidence_tokens=model.min_evidence_tokens,
            is_active=model.is_active,
        )

    @staticmethod
    def _to_chunking(model: ChunkingConfigurationModel) -> ChunkingConfig:
        return ChunkingConfig(
            config_id=model.id,
            strategy=model.strategy,
            target_chunk_tokens=model.target_chunk_tokens,
            min_chunk_tokens=model.min_chunk_tokens,
            max_chunk_tokens=model.max_chunk_tokens,
            overlap_tokens=model.overlap_tokens,
            table_as_unit=model.table_as_unit,
            procedure_grouping=model.procedure_grouping,
            is_active=model.is_active,
        )
