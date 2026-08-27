"""Validated, secret-free AI and retrieval configuration values."""

from dataclasses import dataclass
from urllib.parse import urlparse

CHUNKING_STRATEGIES = frozenset({"SEMANTIC_STRUCTURE", "FIXED_SIZE"})


def _validate_endpoint(endpoint: str) -> None:
    parsed = urlparse(endpoint)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise ValueError("Configuration endpoint must be an absolute HTTP(S) URL")


@dataclass(frozen=True, slots=True)
class LLMConfig:
    provider: str
    model: str
    endpoint: str
    temperature: float = 0.1
    max_tokens: int = 2048
    context_window: int = 4096
    timeout_seconds: int = 30
    max_retries: int = 2
    extra_params: tuple[tuple[str, str], ...] = ()
    is_active: bool = True
    label: str | None = None
    api_key_configured: bool = False
    config_id: str | None = None

    def __post_init__(self) -> None:
        if not self.provider.strip() or not self.model.strip():
            raise ValueError("LLM provider and model are required")
        _validate_endpoint(self.endpoint)
        if not 0 <= self.temperature <= 2:
            raise ValueError("LLM temperature must be between zero and two")
        if self.max_tokens < 1 or self.context_window < 1 or not 1 <= self.timeout_seconds <= 600:
            raise ValueError("LLM token and timeout values must be positive")
        if not 0 <= self.max_retries <= 5:
            raise ValueError("LLM retries must be between zero and five")


@dataclass(frozen=True, slots=True)
class EmbeddingConfig:
    provider: str
    model: str
    model_version: str
    endpoint: str
    dimensions: int
    index_compat_id: str
    config_id: str | None = None
    distance_method: str = "cosine"
    batch_size: int = 32
    timeout_seconds: int = 30
    is_active: bool = True
    label: str | None = None
    api_key_configured: bool = False

    def __post_init__(self) -> None:
        if not self.provider.strip() or not self.model.strip() or not self.model_version.strip():
            raise ValueError("Embedding provider, model, and version are required")
        _validate_endpoint(self.endpoint)
        if self.dimensions < 1 or self.batch_size < 1 or not 1 <= self.timeout_seconds <= 600:
            raise ValueError("Embedding dimensions, batch size, and timeout must be positive")
        if self.distance_method not in {"cosine", "dot_product", "euclidean"}:
            raise ValueError("Unsupported embedding distance method")
        if not self.index_compat_id.strip():
            raise ValueError("Embedding index compatibility identity is required")

    @property
    def embedding_model_id(self) -> str:
        return self.index_compat_id


@dataclass(frozen=True, slots=True)
class RetrievalConfig:
    top_k_candidates: int = 20
    final_top_k: int = 5
    similarity_threshold: float = 0.40
    dense_weight: float = 0.70
    sparse_weight: float = 0.30
    rerank_enabled: bool = False
    rerank_top_k: int = 20
    exact_id_boost: bool = True
    min_evidence_tokens: int = 100
    config_id: str | None = None
    is_active: bool = True

    def __post_init__(self) -> None:
        if (
            self.top_k_candidates < 1
            or self.final_top_k < 1
            or self.final_top_k > self.top_k_candidates
        ):
            raise ValueError("Retrieval top-k values are invalid")
        if not 0 <= self.similarity_threshold <= 1:
            raise ValueError("Similarity threshold must be between zero and one")
        if (
            self.dense_weight < 0
            or self.sparse_weight < 0
            or abs(self.dense_weight + self.sparse_weight - 1) > 1e-9
        ):
            raise ValueError("Retrieval weights must be non-negative and non-zero")
        if self.rerank_top_k < 1 or self.min_evidence_tokens < 1:
            raise ValueError("Rerank and evidence limits must be positive")


@dataclass(frozen=True, slots=True)
class ChunkingConfig:
    strategy: str = "SEMANTIC_STRUCTURE"
    target_chunk_tokens: int = 512
    min_chunk_tokens: int = 64
    max_chunk_tokens: int = 1024
    overlap_tokens: int = 64
    table_as_unit: bool = True
    procedure_grouping: bool = True
    config_id: str | None = None
    is_active: bool = True

    def __post_init__(self) -> None:
        if self.strategy not in CHUNKING_STRATEGIES:
            raise ValueError("Unsupported chunking strategy")
        if not 1 <= self.min_chunk_tokens <= self.target_chunk_tokens <= self.max_chunk_tokens:
            raise ValueError("Chunk size bounds are invalid")
        if not 0 <= self.overlap_tokens < self.target_chunk_tokens:
            raise ValueError("Chunk overlap must be within the maximum chunk size")


@dataclass(frozen=True, slots=True)
class ConfigurationSnapshot:
    """One immutable set of settings captured at request or job start."""

    llm: LLMConfig
    embedding: EmbeddingConfig
    retrieval: RetrievalConfig
    chunking: ChunkingConfig


@dataclass(frozen=True, slots=True)
class ConfigurationValidation:
    configuration: ConfigurationSnapshot
    requires_reindex: bool = False
    reindex_reasons: tuple[str, ...] = ()

    @property
    def llm(self) -> LLMConfig:
        return self.configuration.llm

    @property
    def embedding(self) -> EmbeddingConfig:
        return self.configuration.embedding

    @property
    def retrieval(self) -> RetrievalConfig:
        return self.configuration.retrieval

    @property
    def chunking(self) -> ChunkingConfig:
        return self.configuration.chunking


__all__ = [
    "CHUNKING_STRATEGIES",
    "ChunkingConfig",
    "ConfigurationSnapshot",
    "ConfigurationValidation",
    "EmbeddingConfig",
    "LLMConfig",
    "RetrievalConfig",
]
