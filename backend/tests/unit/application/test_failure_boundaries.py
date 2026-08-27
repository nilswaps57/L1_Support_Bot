import httpx
import pytest

from l1_support_bot.application.shared.failure_mapping import map_infrastructure_error
from l1_support_bot.application.shared.retry_policy import RetryPolicy, run_with_retry
from l1_support_bot.domain.errors import (
    DatabaseUnavailableError,
    EmbeddingUnavailableError,
    LLMUnavailableError,
    RetryExhaustedError,
    ServiceUnavailableError,
    VectorStoreUnavailableError,
)


@pytest.mark.asyncio
async def test_transient_idempotent_operation_is_bounded_and_maps_retry_exhaustion() -> None:
    attempts = 0

    async def operation() -> None:
        nonlocal attempts
        attempts += 1
        raise httpx.ConnectError("password=/private/secret endpoint=internal")

    with pytest.raises(RetryExhaustedError):
        await run_with_retry(operation, policy=RetryPolicy(max_attempts=2), idempotent=True)

    assert attempts == 2
    mapped = map_infrastructure_error(RetryExhaustedError(), service="llm")
    assert mapped.code == "RETRY_EXHAUSTED"
    assert "secret" not in mapped.safe_message


@pytest.mark.asyncio
async def test_non_idempotent_operation_is_never_retried() -> None:
    attempts = 0

    async def operation() -> None:
        nonlocal attempts
        attempts += 1
        raise httpx.ReadTimeout("database password and SQL details")

    with pytest.raises(httpx.ReadTimeout):
        await run_with_retry(operation, policy=RetryPolicy(max_attempts=4), idempotent=False)

    assert attempts == 1


def test_deterministic_failures_are_not_transient() -> None:
    from l1_support_bot.application.shared.retry_policy import is_transient_failure

    assert not is_transient_failure(ValueError("invalid input"))
    assert is_transient_failure(TimeoutError())


@pytest.mark.parametrize(
    ("service", "error_type", "code"),
    [
        ("llm", LLMUnavailableError, "LLM_UNAVAILABLE"),
        ("embedding", EmbeddingUnavailableError, "EMBEDDING_UNAVAILABLE"),
        ("vector_store", VectorStoreUnavailableError, "VECTOR_STORE_UNAVAILABLE"),
        ("database", DatabaseUnavailableError, "DATABASE_UNAVAILABLE"),
    ],
)
def test_infrastructure_categories_remain_public_and_sanitized(
    service: str, error_type: type[Exception], code: str
) -> None:
    mapped = map_infrastructure_error(
        RuntimeError("traceback /srv/app prompt=secret SQL select * from users"),
        service=service,
    )

    assert isinstance(mapped, error_type)
    assert mapped.code == code
    assert "srv" not in mapped.safe_message
    assert "secret" not in mapped.safe_message
    assert "SQL" not in mapped.safe_message


def test_unknown_infrastructure_failure_has_generic_safe_mapping() -> None:
    mapped = map_infrastructure_error(
        RuntimeError("credentials=top-secret /home/labuser/app.db"), service="unknown"
    )

    assert isinstance(mapped, ServiceUnavailableError)
    assert mapped.code == "SERVICE_UNAVAILABLE"
    assert mapped.safe_message == "The requested service is temporarily unavailable."
    assert mapped.details == {}
