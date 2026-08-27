"""Versioned API router registration."""

from fastapi import APIRouter

from l1_support_bot.interface.api.routers import (
	chat,
	configuration,
	documents,
	feedback,
	health,
	ingestion,
	sessions,
)

api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(documents.router)
api_router.include_router(ingestion.router)
api_router.include_router(chat.router)
api_router.include_router(feedback.router)
api_router.include_router(sessions.router)
api_router.include_router(configuration.router)
