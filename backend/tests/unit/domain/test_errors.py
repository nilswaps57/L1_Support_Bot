from l1_support_bot.domain.errors import (
    DomainError,
    ErrorCategory,
    IncompatibleIndexError,
    InsufficientEvidenceError,
    ServiceUnavailableError,
)


def test_domain_errors_expose_safe_codes_and_categories() -> None:
    error = ServiceUnavailableError("Embedding service is unavailable.")

    assert isinstance(error, DomainError)
    assert error.category is ErrorCategory.UNAVAILABLE_SERVICE
    assert error.code == "SERVICE_UNAVAILABLE"
    assert "password" not in error.safe_message.lower()


def test_specialized_errors_have_stable_codes() -> None:
    assert InsufficientEvidenceError().code == "INSUFFICIENT_EVIDENCE"
    assert IncompatibleIndexError().code == "INCOMPATIBLE_INDEX"