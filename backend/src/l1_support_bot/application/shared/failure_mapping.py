"""Map infrastructure failures to the public, safe domain taxonomy."""

from __future__ import annotations

from l1_support_bot.domain.errors import (
    DatabaseUnavailableError,
    DomainError,
    EmbeddingUnavailableError,
    LLMUnavailableError,
    ServiceUnavailableError,
    VectorStoreUnavailableError,
)


def map_infrastructure_error(error: BaseException, *, service: str) -> DomainError:
    """Return a safe category without copying provider or infrastructure details."""

    if isinstance(error, DomainError):
        return error
    if service == "llm":
        return LLMUnavailableError()
    if service == "embedding":
        return EmbeddingUnavailableError()
    if service == "vector_store":
        return VectorStoreUnavailableError()
    if service == "database":
        return DatabaseUnavailableError()
    if isinstance(error, TimeoutError) or type(error).__name__.lower().endswith("timeoutexception"):
        return ServiceUnavailableError(
            "The requested service did not respond in time.",
            details={"failure_type": "timeout"},
        )
    return ServiceUnavailableError("The requested service is temporarily unavailable.")