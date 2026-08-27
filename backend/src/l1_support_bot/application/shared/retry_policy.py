"""Bounded retry policy for transient, idempotent infrastructure work."""

from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from typing import TypeVar

from l1_support_bot.domain.errors import RetryExhaustedError

ResultT = TypeVar("ResultT")


@dataclass(frozen=True, slots=True)
class RetryPolicy:
    max_attempts: int = 3
    delay_seconds: float = 0.0

    def __post_init__(self) -> None:
        if self.max_attempts < 1:
            raise ValueError("Retry attempts must be positive")
        if self.delay_seconds < 0:
            raise ValueError("Retry delay cannot be negative")


def is_transient_failure(error: BaseException) -> bool:
    """Return true only for failures that may succeed on a later attempt."""

    if isinstance(
        error, (TimeoutError, ConnectionError, OSError)
    ):
        return True
    if type(error).__name__.lower() in {
        "connecterror",
        "networkerror",
        "timeoutexception",
        "readtimeout",
        "connecttimeout",
        "pooltimeout",
    }:
        return True
    response = getattr(error, "response", None)
    status_code = getattr(response, "status_code", None)
    if isinstance(status_code, int):
        return status_code in {408, 425, 429, 500, 502, 503, 504}
    return False


async def run_with_retry(
    operation: Callable[[], Awaitable[ResultT]],
    *,
    policy: RetryPolicy,
    idempotent: bool,
) -> ResultT:
    """Retry a transient operation within a strict attempt bound."""

    attempts = policy.max_attempts if idempotent else 1
    last_error: BaseException | None = None
    for attempt in range(attempts):
        try:
            return await operation()
        except Exception as error:
            last_error = error
            if not idempotent or not is_transient_failure(error):
                raise
            if attempt + 1 >= attempts:
                raise RetryExhaustedError() from error
            if policy.delay_seconds:
                await asyncio.sleep(policy.delay_seconds)
    raise RetryExhaustedError() from last_error