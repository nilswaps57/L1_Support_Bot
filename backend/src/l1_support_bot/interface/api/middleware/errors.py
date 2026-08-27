"""Translate domain and HTTP failures to the public safe error contract."""

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from l1_support_bot.domain.errors import DomainError, ErrorCategory
from l1_support_bot.interface.dto.errors import ErrorResponse
from l1_support_bot.interface.logging import log_failure

_SAFE_MESSAGES = {
    "LLM_CONNECTIVITY_FAILED": "The configured LLM endpoint could not be validated.",
    "EMBEDDING_CONNECTIVITY_FAILED": "The configured embedding endpoint could not be validated.",
    "REINDEX_REQUIRED": "This change requires a successful re-index before activation.",
    "INVALID_CITATION": "The answer could not be validated against the available sources.",
    "LLM_UNAVAILABLE": "Answer generation is temporarily unavailable.",
    "EMBEDDING_UNAVAILABLE": "Embedding service is temporarily unavailable.",
    "VECTOR_STORE_UNAVAILABLE": "Vector search is temporarily unavailable.",
    "DATABASE_UNAVAILABLE": "Metadata persistence is temporarily unavailable.",
    "RETRY_EXHAUSTED": "The requested service remains unavailable after a safe retry.",
    "SERVICE_UNAVAILABLE": "The requested service is temporarily unavailable.",
    "INTERNAL_ERROR": "An unexpected error occurred.",
}
_SAFE_DETAIL_KEYS = {
    "supported_extensions",
    "expected_file_type",
    "max_size_bytes",
    "current_status",
    "indexed_documents",
    "confirmation_required",
}


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
    safe_details = {
        key: value
        for key, value in (details or {}).items()
        if key in _SAFE_DETAIL_KEYS and isinstance(value, (str, int, float, bool))
    }
    payload = ErrorResponse(
        error_code=error_code,
        message=_SAFE_MESSAGES.get(error_code, message),
        request_id=_request_id(request),
        details=safe_details,
    )
    return JSONResponse(status_code=status_code, content=payload.model_dump(mode="json"))


async def domain_error_handler(request: Request, exc: Exception) -> JSONResponse:
    error = exc if isinstance(exc, DomainError) else DomainError("Request could not be completed.")
    log_failure(category=error.code)
    return _response(
        request,
        status_code=(
            503
            if error.category is ErrorCategory.UNAVAILABLE_SERVICE
            else 500
            if error.code == "DOCUMENT_CLEANUP_FAILED"
            else 404
            if error.code == "SESSION_NOT_FOUND"
            else 409
            if error.code in {
                "DUPLICATE_DOCUMENT",
                "DOCUMENT_IN_PROCESSING",
                "DOCUMENT_NOT_DELETABLE",
                "REINDEX_REQUIRED",
            }
            else 422
            if error.code in {"LLM_CONNECTIVITY_FAILED", "EMBEDDING_CONNECTIVITY_FAILED"}
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
    log_failure(category="INTERNAL_ERROR")
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