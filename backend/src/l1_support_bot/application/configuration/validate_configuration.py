"""Cross-category validation before configuration can be activated."""

from l1_support_bot.domain.models.configuration import (
    ChunkingConfig,
    ConfigurationSnapshot,
    ConfigurationValidation,
    EmbeddingConfig,
    LLMConfig,
    RetrievalConfig,
)


def validate_configuration(
    *,
    llm: LLMConfig,
    embedding: EmbeddingConfig,
    retrieval: RetrievalConfig,
    chunking: ChunkingConfig,
) -> ConfigurationValidation:
    """Return one immutable set of settings after all cross-field checks."""

    if retrieval.rerank_enabled and retrieval.rerank_top_k > retrieval.top_k_candidates:
        raise ValueError("Rerank top-k cannot exceed candidate top-k")
    return ConfigurationValidation(
        configuration=ConfigurationSnapshot(
            llm=llm,
            embedding=embedding,
            retrieval=retrieval,
            chunking=chunking,
        )
    )
