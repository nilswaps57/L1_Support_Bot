"""Structured logging and request context without sensitive payloads."""

import logging
from collections.abc import Iterator
from contextlib import contextmanager
from contextvars import ContextVar
from dataclasses import dataclass
from typing import cast
from uuid import UUID

import structlog


@dataclass(frozen=True, slots=True)
class RequestContext:
    request_id: UUID
    correlation_id: UUID


_request_context: ContextVar[RequestContext | None] = ContextVar("request_context", default=None)


def configure_logging(level: str = "INFO") -> None:
    logging.basicConfig(format="%(message)s", level=getattr(logging, level.upper(), logging.INFO))
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso", utc=True),
            structlog.processors.JSONRenderer(),
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )


def get_logger(name: str = "l1_support_bot") -> structlog.stdlib.BoundLogger:
    return cast(structlog.stdlib.BoundLogger, structlog.get_logger(name))


def log_failure(*, category: str, duration_ms: int | None = None) -> None:
    """Log failure metadata only; never log exception text, prompts, or payloads."""

    fields: dict[str, object] = {"error_category": category}
    if duration_ms is not None:
        fields["duration_ms"] = duration_ms
    get_logger().warning("request_failed", **fields)


def log_security_event(*, category: str, outcome: str) -> None:
    """Log only aggregate security metadata; prompt and document content stay out of logs."""

    get_logger().warning(
        "security_event",
        security_category=category,
        outcome=outcome,
    )


def bind_request_context(*, request_id: str, correlation_id: str) -> RequestContext:
    context = RequestContext(UUID(request_id), UUID(correlation_id))
    _request_context.set(context)
    structlog.contextvars.bind_contextvars(
        request_id=str(context.request_id), correlation_id=str(context.correlation_id)
    )
    return context


def get_request_context() -> RequestContext | None:
    return _request_context.get()


def clear_request_context() -> None:
    _request_context.set(None)
    structlog.contextvars.clear_contextvars()


@contextmanager
def request_context(*, request_id: str, correlation_id: str) -> Iterator[RequestContext]:
    context = bind_request_context(request_id=request_id, correlation_id=correlation_id)
    try:
        yield context
    finally:
        clear_request_context()