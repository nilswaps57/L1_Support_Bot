"""Public configuration DTOs. Secrets, endpoints, and persistence IDs are excluded."""

from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

PositiveInt = Annotated[int, Field(ge=1)]


class LLMConfigRequest(BaseModel):
    provider: Literal["ollama", "openai", "azure_openai", "fake"]
    model: str
    endpoint: str | None = None
    temperature: float = Field(default=0.1, ge=0, le=2)
    max_tokens: PositiveInt = 2048
    context_window: PositiveInt = 4096
    timeout_seconds: PositiveInt = 30
    max_retries: int = Field(default=2, ge=0, le=5)
    label: str | None = Field(default=None, max_length=200)
    api_key: str | None = Field(default=None, min_length=1, repr=False)
    api_key_env_var: str | None = Field(default=None, max_length=200)


class LLMConfigResponse(BaseModel):
    provider: str
    model: str
    temperature: float
    max_tokens: int
    context_window: int
    timeout_seconds: int
    max_retries: int
    label: str | None
    api_key_configured: bool
    status: str = "active"


class EmbeddingConfigRequest(BaseModel):
    provider: Literal["openai_compatible", "ollama", "fake", "test"]
    model: str
    model_version: str = "dev"
    endpoint: str | None = None
    dimensions: PositiveInt
    distance_method: str = "cosine"
    index_compat_id: str
    batch_size: PositiveInt = 32
    timeout_seconds: PositiveInt = 30
    label: str | None = Field(default=None, max_length=200)
    api_key: str | None = Field(default=None, min_length=1, repr=False)
    api_key_env_var: str | None = Field(default=None, max_length=200)
    confirm_reindex: bool = False


class EmbeddingConfigResponse(BaseModel):
    provider: str
    model: str
    model_version: str
    dimensions: int
    distance_method: str
    index_compatible: bool
    batch_size: int
    timeout_seconds: int
    label: str | None
    api_key_configured: bool
    status: str = "active"


class RetrievalConfigRequest(BaseModel):
    top_k_candidates: PositiveInt = 20
    final_top_k: PositiveInt = 5
    similarity_threshold: float = Field(default=0.4, ge=0, le=1)
    dense_weight: float = Field(default=0.7, ge=0, le=1)
    sparse_weight: float = Field(default=0.3, ge=0, le=1)
    rerank_enabled: bool = False
    rerank_top_k: PositiveInt = 20
    exact_id_boost: bool = True
    min_evidence_tokens: PositiveInt = 100

    @model_validator(mode="after")
    def validate_relationships(self) -> "RetrievalConfigRequest":
        if self.final_top_k > self.top_k_candidates:
            raise ValueError("final_top_k cannot exceed top_k_candidates")
        if self.rerank_enabled and self.rerank_top_k > self.top_k_candidates:
            raise ValueError("rerank_top_k cannot exceed top_k_candidates")
        if abs(self.dense_weight + self.sparse_weight - 1) > 1e-9:
            raise ValueError("dense_weight and sparse_weight must total one")
        return self


class RetrievalConfigResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    top_k_candidates: int
    final_top_k: int
    similarity_threshold: float
    dense_weight: float
    sparse_weight: float
    rerank_enabled: bool
    rerank_top_k: int
    exact_id_boost: bool
    min_evidence_tokens: int
    status: str = "active"


class ChunkingConfigRequest(BaseModel):
    strategy: str = "SEMANTIC_STRUCTURE"
    target_chunk_tokens: PositiveInt = 512
    min_chunk_tokens: PositiveInt = 64
    max_chunk_tokens: PositiveInt = 1024
    overlap_tokens: int = Field(default=64, ge=0)
    table_as_unit: bool = True
    procedure_grouping: bool = True
    confirm_reindex: bool = False


class ChunkingConfigResponse(BaseModel):
    strategy: str
    target_chunk_tokens: int
    min_chunk_tokens: int
    max_chunk_tokens: int
    overlap_tokens: int
    table_as_unit: bool
    procedure_grouping: bool
    status: str = "active"


class ConnectivityResponse(BaseModel):
    category: str
    status: str
    model: str
    latency_ms: int


class ActivationResponse(BaseModel):
    status: str
    requires_reindex: bool = False
    reindex_reasons: tuple[str, ...] = ()
