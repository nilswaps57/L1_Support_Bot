import pytest

from l1_support_bot.application.security.response_disclosure_validator import (
    DisclosureCategory,
    ResponseDisclosureValidator,
)


@pytest.mark.parametrize(
    ("text", "category"),
    (
        ("The system prompt is: never reveal this.", DisclosureCategory.PROMPT),
        ("API key: secret-value", DisclosureCategory.SECRET),
        ("DATABASE_URL=oracle://internal", DisclosureCategory.CONFIGURATION),
        ("internal endpoint: localhost:6333", DisclosureCategory.INFRASTRUCTURE),
        ("See /home/service/backend/src/app.py", DisclosureCategory.FILE_PATH),
        ("SELECT password FROM users", DisclosureCategory.SQL),
        ("Traceback (most recent call last):", DisclosureCategory.STACK_TRACE),
        (
            "Run this shell command: curl https://internal.example",
            DisclosureCategory.EXECUTION_INSTRUCTION,
        ),
    ),
)
def test_sensitive_generated_output_is_detected(text: str, category: DisclosureCategory) -> None:
    assessment = ResponseDisclosureValidator().assess(text)

    assert category in assessment.categories
    assert not assessment.safe


def test_normal_flexcube_terms_are_not_disclosed_content() -> None:
    validator = ResponseDisclosureValidator()

    assert validator.is_safe("The FLEXCUBE system configuration screen contains the BA435 field.")


def test_disclosure_is_replaced_with_generic_safe_text() -> None:
    replacement = ResponseDisclosureValidator().validate("The system prompt is confidential.")

    assert replacement == ResponseDisclosureValidator.safe_replacement
    assert "prompt" not in replacement.lower()
