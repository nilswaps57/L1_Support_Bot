"""FastAPI application factory and composition root."""

from fastapi import FastAPI

from l1_support_bot.infrastructure.composition import build_default_dependencies
from l1_support_bot.interface.api.middleware.cors import add_cors_middleware
from l1_support_bot.interface.api.middleware.errors import register_error_handlers
from l1_support_bot.interface.api.middleware.request_context import add_request_context_middleware
from l1_support_bot.interface.api.routers import api_router
from l1_support_bot.interface.config import Settings, get_settings
from l1_support_bot.interface.dependencies import PortDependencies, install_dependencies
from l1_support_bot.interface.logging import configure_logging


def create_app(
    settings: Settings | None = None,
    dependencies: PortDependencies | None = None,
) -> FastAPI:
    resolved_settings = settings or get_settings()
    configure_logging(resolved_settings.log_level)
    app = FastAPI(title=resolved_settings.app_name, version=resolved_settings.app_version)
    app.state.settings = resolved_settings
    if dependencies is None:
        engine, resolved_dependencies = build_default_dependencies(resolved_settings)
        app.state.database_engine = engine
    else:
        resolved_dependencies = dependencies
    install_dependencies(app, resolved_dependencies)
    add_cors_middleware(app, resolved_settings.cors_allowed_origins)
    add_request_context_middleware(
        app, max_body_bytes=resolved_settings.max_request_body_bytes
    )
    register_error_handlers(app)
    app.include_router(api_router, prefix="/api/v1")
    return app


app = create_app()