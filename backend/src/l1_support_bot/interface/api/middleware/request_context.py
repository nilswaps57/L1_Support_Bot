"""Request identifiers and bounded request-body middleware."""

from uuid import UUID, uuid4

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from l1_support_bot.interface.dto.errors import ErrorResponse
from l1_support_bot.interface.logging import bind_request_context, clear_request_context


def _valid_or_new(value: str | None) -> UUID:
    try:
        return UUID(value) if value else uuid4()
    except ValueError:
        return uuid4()


def add_request_context_middleware(app: FastAPI, *, max_body_bytes: int) -> None:
    @app.middleware("http")
    async def request_context_middleware(request: Request, call_next):  # type: ignore[no-untyped-def]
        request_id = _valid_or_new(request.headers.get("X-Request-ID"))
        correlation_id = _valid_or_new(request.headers.get("X-Correlation-ID"))
        request.state.request_id = request_id
        request.state.correlation_id = correlation_id
        bind_request_context(request_id=str(request_id), correlation_id=str(correlation_id))
        try:
            body = await request.body()
            if len(body) > max_body_bytes:
                payload = ErrorResponse(
                    error_code="REQUEST_TOO_LARGE",
                    message="Request body exceeds the configured limit.",
                    request_id=str(request_id),
                )
                response = JSONResponse(status_code=413, content=payload.model_dump(mode="json"))
            else:
                response = await call_next(request)
            response.headers["X-Request-ID"] = str(request_id)
            response.headers["X-Correlation-ID"] = str(correlation_id)
            return response
        finally:
            clear_request_context()