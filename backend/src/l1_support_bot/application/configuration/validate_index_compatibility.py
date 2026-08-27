"""Determine whether a proposed configuration can use the active index."""

from dataclasses import dataclass

from l1_support_bot.domain.models.configuration import ChunkingConfig, EmbeddingConfig


@dataclass(frozen=True, slots=True)
class IndexCompatibilityResult:
    requires_reindex: bool
    reasons: tuple[str, ...] = ()
    indexed_documents: int = 0


def check_index_compatibility(
    *,
    current_embedding: EmbeddingConfig,
    proposed_embedding: EmbeddingConfig,
    current_chunking: ChunkingConfig,
    proposed_chunking: ChunkingConfig,
    indexed_documents: int,
) -> IndexCompatibilityResult:
    reasons: list[str] = []
    current_embedding_identity = (
        current_embedding.provider,
        current_embedding.model,
        current_embedding.model_version,
        current_embedding.dimensions,
        current_embedding.distance_method,
        current_embedding.index_compat_id,
    )
    proposed_embedding_identity = (
        proposed_embedding.provider,
        proposed_embedding.model,
        proposed_embedding.model_version,
        proposed_embedding.dimensions,
        proposed_embedding.distance_method,
        proposed_embedding.index_compat_id,
    )
    if current_embedding_identity != proposed_embedding_identity:
        reasons.append("embedding configuration is incompatible with the active index")
    current_chunking_identity = (
        current_chunking.strategy,
        current_chunking.target_chunk_tokens,
        current_chunking.min_chunk_tokens,
        current_chunking.max_chunk_tokens,
        current_chunking.overlap_tokens,
        current_chunking.table_as_unit,
        current_chunking.procedure_grouping,
    )
    proposed_chunking_identity = (
        proposed_chunking.strategy,
        proposed_chunking.target_chunk_tokens,
        proposed_chunking.min_chunk_tokens,
        proposed_chunking.max_chunk_tokens,
        proposed_chunking.overlap_tokens,
        proposed_chunking.table_as_unit,
        proposed_chunking.procedure_grouping,
    )
    if current_chunking_identity != proposed_chunking_identity:
        reasons.append("chunking configuration changes the indexed chunk boundaries")
    return IndexCompatibilityResult(
        requires_reindex=bool(reasons),
        reasons=tuple(reasons),
        indexed_documents=indexed_documents,
    )
