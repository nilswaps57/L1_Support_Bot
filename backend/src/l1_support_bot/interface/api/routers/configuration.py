"""Configuration API with fail-closed writes and secret-free responses."""

from fastapi import APIRouter, Request

from l1_support_bot.application.configuration.update_configuration import UpdateConfiguration
from l1_support_bot.application.configuration.validate_embedding import ValidateEmbedding
from l1_support_bot.application.configuration.validate_llm import ValidateLLM
from l1_support_bot.domain.errors import ServiceUnavailableError
from l1_support_bot.domain.models.configuration import (
    ChunkingConfig,
    EmbeddingConfig,
    LLMConfig,
    RetrievalConfig,
)
from l1_support_bot.interface.dependencies import ensure_persistence_available, get_dependencies
from l1_support_bot.interface.dto.configuration import (
    ActivationResponse,
    ChunkingConfigRequest,
    ChunkingConfigResponse,
    ConnectivityResponse,
    EmbeddingConfigRequest,
    EmbeddingConfigResponse,
    LLMConfigRequest,
    LLMConfigResponse,
    RetrievalConfigRequest,
    RetrievalConfigResponse,
)

router = APIRouter(prefix="/config", tags=["configuration"])


async def _configs(
    request: Request,
) -> tuple[LLMConfig, EmbeddingConfig, RetrievalConfig, ChunkingConfig]:
    dependencies = get_dependencies(request)
    repository = dependencies.configuration_repository
    cache = dependencies.runtime_configuration_cache
    values: tuple[LLMConfig | None, EmbeddingConfig | None] = (None, None)
    retrieval: RetrievalConfig | None = None
    chunking: ChunkingConfig | None = None
    if repository is None:
        values = None, None
    else:
        try:
            values = await repository.get_llm(), await repository.get_embedding()
            retrieval = await repository.get_retrieval()
            chunking = await repository.get_chunking()
        except Exception:
            values = None, None
            retrieval = None
            chunking = None
    if cache is not None:
        values = values[0] or await cache.get_llm(), values[1] or await cache.get_embedding()
        retrieval = retrieval or await cache.get_retrieval()
        chunking = chunking or await cache.get_chunking()
    llm = values[0] or LLMConfig(
        provider="ollama", model="phi3.5", endpoint="http://localhost:11434"
    )
    embedding = values[1] or EmbeddingConfig(
        provider="ollama",
        model="nomic-embed-text",
        model_version="dev",
        endpoint="http://localhost:11434/v1",
        dimensions=768,
        index_compat_id="ollama:nomic-embed-text:dev:768",
    )
    return llm, embedding, retrieval or RetrievalConfig(), chunking or ChunkingConfig()


def _llm_response(config: LLMConfig) -> LLMConfigResponse:
    return LLMConfigResponse(
        provider=config.provider,
        model=config.model,
        temperature=config.temperature,
        max_tokens=config.max_tokens,
        context_window=config.context_window,
        timeout_seconds=config.timeout_seconds,
        max_retries=config.max_retries,
        label=config.label,
        api_key_configured=config.api_key_configured,
    )


def _embedding_response(
    config: EmbeddingConfig, *, compatible: bool = True
) -> EmbeddingConfigResponse:
    return EmbeddingConfigResponse(
        provider=config.provider,
        model=config.model,
        model_version=config.model_version,
        dimensions=config.dimensions,
        distance_method=config.distance_method,
        index_compatible=compatible,
        batch_size=config.batch_size,
        timeout_seconds=config.timeout_seconds,
        label=config.label,
        api_key_configured=config.api_key_configured,
    )


def _retrieval_response(config: RetrievalConfig) -> RetrievalConfigResponse:
    return RetrievalConfigResponse.model_validate(config, from_attributes=True)


def _chunking_response(config: ChunkingConfig) -> ChunkingConfigResponse:
    return ChunkingConfigResponse.model_validate(config, from_attributes=True)


async def _update(request: Request, *, category: str, values: object) -> ActivationResponse:
    await ensure_persistence_available(request)
    llm, embedding, retrieval, chunking = await _configs(request)
    if category == "llm":
        llm = values  # type: ignore[assignment]
    elif category == "embedding":
        embedding = values  # type: ignore[assignment]
    elif category == "retrieval":
        retrieval = values  # type: ignore[assignment]
    else:
        chunking = values  # type: ignore[assignment]
    dependencies = get_dependencies(request)
    repository = dependencies.configuration_repository
    cache = dependencies.runtime_configuration_cache
    if repository is None or cache is None:
        raise ServiceUnavailableError("Configuration is temporarily unavailable.")
    updater = UpdateConfiguration(
        repository=repository,
        cache=cache,
        llm_validator=(
            ValidateLLM(dependencies.llm) if category == "llm" and dependencies.llm else None
        ),
        embedding_validator=(
            ValidateEmbedding(dependencies.embedding)
            if category == "embedding" and dependencies.embedding
            else None
        ),
    )
    result = await updater.execute(
        llm=llm,
        embedding=embedding,
        retrieval=retrieval,
        chunking=chunking,
    )
    return ActivationResponse(
        status=result.status,
        requires_reindex=result.requires_reindex,
        reindex_reasons=result.reindex_reasons,
    )


@router.get("/llm", response_model=LLMConfigResponse)
async def get_llm_config(request: Request) -> LLMConfigResponse:
    return _llm_response((await _configs(request))[0])


@router.put("/llm", response_model=ActivationResponse)
async def update_llm_config(request: Request, payload: LLMConfigRequest) -> ActivationResponse:
    current = (await _configs(request))[0]
    values = payload.model_dump(exclude={"api_key", "api_key_env_var"})
    values["endpoint"] = payload.endpoint or current.endpoint
    return await _update(request, category="llm", values=LLMConfig(**values))


@router.post("/llm/validate", response_model=ConnectivityResponse)
async def validate_llm_config(request: Request, payload: LLMConfigRequest) -> ConnectivityResponse:
    dependencies = get_dependencies(request)
    if dependencies.llm is None:
        raise ServiceUnavailableError("LLM validation is temporarily unavailable.")
    values = payload.model_dump(exclude={"api_key", "api_key_env_var"})
    values["endpoint"] = payload.endpoint or (await _configs(request))[0].endpoint
    result = await ValidateLLM(dependencies.llm).execute(LLMConfig(**values))
    return ConnectivityResponse(
        category=result.category,
        status=result.status,
        model=result.model,
        latency_ms=result.latency_ms,
    )


@router.get("/embedding", response_model=EmbeddingConfigResponse)
async def get_embedding_config(request: Request) -> EmbeddingConfigResponse:
    return _embedding_response((await _configs(request))[1])


@router.put("/embedding", response_model=ActivationResponse)
async def update_embedding_config(
    request: Request, payload: EmbeddingConfigRequest
) -> ActivationResponse:
    current = (await _configs(request))[1]
    values = payload.model_dump(exclude={"api_key", "api_key_env_var", "confirm_reindex"})
    values["endpoint"] = payload.endpoint or current.endpoint
    return await _update(
        request,
        category="embedding",
        values=EmbeddingConfig(**values),
    )


@router.post("/embedding/validate", response_model=ConnectivityResponse)
async def validate_embedding_config(
    request: Request, payload: EmbeddingConfigRequest
) -> ConnectivityResponse:
    dependencies = get_dependencies(request)
    if dependencies.embedding is None:
        raise ServiceUnavailableError("Embedding validation is temporarily unavailable.")
    values = payload.model_dump(exclude={"api_key", "api_key_env_var", "confirm_reindex"})
    values["endpoint"] = payload.endpoint or (await _configs(request))[1].endpoint
    result = await ValidateEmbedding(dependencies.embedding).execute(EmbeddingConfig(**values))
    return ConnectivityResponse(
        category=result.category,
        status=result.status,
        model=result.model,
        latency_ms=result.latency_ms,
    )


@router.get("/retrieval", response_model=RetrievalConfigResponse)
async def get_retrieval_config(request: Request) -> RetrievalConfigResponse:
    return _retrieval_response((await _configs(request))[2])


@router.put("/retrieval", response_model=ActivationResponse)
async def update_retrieval_config(
    request: Request, payload: RetrievalConfigRequest
) -> ActivationResponse:
    return await _update(
        request, category="retrieval", values=RetrievalConfig(**payload.model_dump())
    )


@router.get("/chunking", response_model=ChunkingConfigResponse)
async def get_chunking_config(request: Request) -> ChunkingConfigResponse:
    return _chunking_response((await _configs(request))[3])


@router.put("/chunking", response_model=ActivationResponse)
async def update_chunking_config(
    request: Request, payload: ChunkingConfigRequest
) -> ActivationResponse:
    return await _update(
        request,
        category="chunking",
        values=ChunkingConfig(**payload.model_dump(exclude={"confirm_reindex"})),
    )
