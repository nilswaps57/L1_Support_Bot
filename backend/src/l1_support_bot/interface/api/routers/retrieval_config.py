"""Retrieval configuration endpoints for Phase 5."""

from fastapi import APIRouter, Request
from pydantic import BaseModel, ConfigDict, Field

from l1_support_bot.domain.errors import ServiceUnavailableError
from l1_support_bot.domain.models.configuration import RetrievalConfig
from l1_support_bot.interface.dependencies import ensure_persistence_available, get_dependencies

router = APIRouter(prefix="/config/retrieval", tags=["configuration"])


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


class RetrievalConfigRequest(RetrievalConfigResponse):
    top_k_candidates: int = Field(default=20, ge=1)
    final_top_k: int = Field(default=5, ge=1)
    similarity_threshold: float = Field(default=0.4, ge=0, le=1)
    dense_weight: float = Field(default=0.7, ge=0, le=1)
    sparse_weight: float = Field(default=0.3, ge=0, le=1)
    rerank_enabled: bool = False
    rerank_top_k: int = Field(default=20, ge=1)
    exact_id_boost: bool = True
    min_evidence_tokens: int = Field(default=100, ge=1)


def _response(config: RetrievalConfig) -> RetrievalConfigResponse:
    return RetrievalConfigResponse.model_validate(config, from_attributes=True)


@router.get("", response_model=RetrievalConfigResponse)
async def get_retrieval_config(request: Request) -> RetrievalConfigResponse:
    repository = get_dependencies(request).configuration_repository
    if repository is None or not hasattr(repository, "get_retrieval"):
        return _response(RetrievalConfig())
    config = await repository.get_retrieval()
    return _response(config or RetrievalConfig())


@router.put("", response_model=RetrievalConfigResponse)
async def save_retrieval_config(
    request: Request, payload: RetrievalConfigRequest
) -> RetrievalConfigResponse:
    await ensure_persistence_available(request)
    repository = get_dependencies(request).configuration_repository
    if repository is None or not hasattr(repository, "save_retrieval"):
        raise ServiceUnavailableError("Retrieval configuration is temporarily unavailable.")
    config = RetrievalConfig(**payload.model_dump())
    return _response(await repository.save_retrieval(config))
