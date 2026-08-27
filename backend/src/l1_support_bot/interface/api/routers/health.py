"""Health endpoint."""

from fastapi import APIRouter, Request

from l1_support_bot.application.configuration.runtime_health import RuntimeHealthState
from l1_support_bot.interface.config import Settings
from l1_support_bot.interface.dependencies import get_dependencies
from l1_support_bot.interface.dto.health import HealthResponse

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
async def health(request: Request) -> HealthResponse:
    settings: Settings = request.app.state.settings
    dependencies = get_dependencies(request)
    cache = dependencies.runtime_configuration_cache
    if cache is not None:
        try:
            await cache.refresh()
        except Exception:
            pass
    state = getattr(cache, "health", RuntimeHealthState())
    return HealthResponse(
        status="degraded" if state.degraded else "healthy",
        version=settings.app_version,
        database=state.database,
        vector_store=state.vector_store,
        llm=state.llm,
        embedding=state.embedding,
        degraded_capabilities=state.degraded_capabilities,
        capabilities={
            "chat": state.llm == "available" and state.vector_store == "available",
            "document_management": state.persistence_available,
            "configuration_mutations": state.persistence_available,
            "feedback_submission": state.persistence_available,
        },
    )
