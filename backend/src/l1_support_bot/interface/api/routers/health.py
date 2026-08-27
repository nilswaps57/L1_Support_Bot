"""Health endpoint."""

from fastapi import APIRouter, Request

from l1_support_bot.interface.config import Settings
from l1_support_bot.interface.dto.health import HealthResponse

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
async def health(request: Request) -> HealthResponse:
    settings: Settings = request.app.state.settings
    return HealthResponse(
        status="healthy",
        version=settings.app_version,
        database="available",
        vector_store="available",
        llm="available",
        embedding="available",
    )
