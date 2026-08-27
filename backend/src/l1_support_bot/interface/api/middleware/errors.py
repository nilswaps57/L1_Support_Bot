"""Translate domain and HTTP failures to the public safe error contract."""

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from l1_support_bot.domain.errors import DomainError, ErrorCategory
from l1_support_bot.interface.dto.errors import ErrorResponse


def _request_id(request: Request) -> str:
    return str(getattr(request.state, "request_id", "unknown"))


def _response(
    request: Request,
    *,
    status_code: int,
    error_code: str,
    message: str,
    details: dict[str, object] | None = None,
) -> JSONResponse:
    payload = ErrorResponse(
        error_code=error_code,
        message=message,
        request_id=_request_id(request),
        details=details or {},
    )
    return JSONResponse(status_code=status_code, content=payload.model_dump(mode="json"))


async def domain_error_handler(request: Request, exc: Exception) -> JSONResponse:
    error = exc if isinstance(exc, DomainError) else DomainError("Request could not be completed.")
    return _response(
        request,
        status_code=(
            503
            if error.category is ErrorCategory.UNAVAILABLE_SERVICE
            else 409
            if error.code in {"DUPLICATE_DOCUMENT", "DOCUMENT_IN_PROCESSING"}
            else 400
        ),
        error_code=error.code,
        message=error.safe_message,
        details=dict(error.details),
    )


async def validation_error_handler(request: Request, exc: Exception) -> JSONResponse:
    del exc
    return _response(
        request,
        status_code=422,
        error_code="VALIDATION_ERROR",
        message="The request contains invalid values.",
    )


async def http_error_handler(request: Request, exc: Exception) -> JSONResponse:
    error = exc if isinstance(exc, StarletteHTTPException) else None
    status_code = error.status_code if error else 500
    message = "The requested resource was not found." if status_code == 404 else "Request failed."
    return _response(
        request,
        status_code=status_code,
        error_code=f"HTTP_{status_code}",
        message=message,
    )


async def unexpected_error_handler(request: Request, exc: Exception) -> JSONResponse:
    del exc
    return _response(
        request,
        status_code=500,
        error_code="INTERNAL_ERROR",
        message="An unexpected error occurred.",
    )


def register_error_handlers(app: FastAPI) -> None:
    app.add_exception_handler(DomainError, domain_error_handler)
    app.add_exception_handler(RequestValidationError, validation_error_handler)
    app.add_exception_handler(StarletteHTTPException, http_error_handler)
    app.add_exception_handler(Exception, unexpected_error_handler)