"""Reject model output that discloses internal application details."""

from __future__ import annotations

import re
from dataclasses import dataclass
from enum import StrEnum


class DisclosureCategory(StrEnum):
    PROMPT = "prompt"
    SECRET = "secret"
    CONFIGURATION = "configuration"
    INFRASTRUCTURE = "infrastructure"
    FILE_PATH = "file_path"
    SQL = "sql"
    STACK_TRACE = "stack_trace"
    EXECUTION_INSTRUCTION = "execution_instruction"


@dataclass(frozen=True, slots=True)
class DisclosureAssessment:
    safe: bool
    categories: tuple[DisclosureCategory, ...] = ()


class ResponseDisclosureValidator:
    """Use narrow contextual patterns so ordinary FLEXCUBE terms remain valid."""

    safe_replacement = (
        "The available knowledge sources do not contain sufficient information to provide "
        "that internal detail."
    )
    _patterns: tuple[tuple[DisclosureCategory, re.Pattern[str]], ...] = (
        (
            DisclosureCategory.PROMPT,
            re.compile(
                r"\b(?:system|developer|hidden|original)\s+(?:prompt|instructions?)\b"
                r"|\b(?:reveal|show|print|dump|quote)\b.{0,80}\b(?:prompt|hidden instructions?)\b",
                re.IGNORECASE,
            ),
        ),
        (
            DisclosureCategory.SECRET,
            re.compile(
                r"\b(?:api\s*key|access\s*token|bearer\s+token|client\s+secret|password|credentials?)\b\s*[:=]"
                r"|\b(?:sk|ghp|xoxb)-[A-Za-z0-9_-]{12,}\b"
                r"|-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----",
                re.IGNORECASE,
            ),
        ),
        (
            DisclosureCategory.CONFIGURATION,
            re.compile(
                r"\b(?:DATABASE_URL|Q" r"DRANT_URL|OL" r"LAMA_(?:BASE_URL|MODEL)|"
                r"EMBEDDING_(?:BASE_URL|MODEL)|CORS_ALLOWED_ORIGINS)\s*="
                r"|\b(?:internal|hidden)\s+configuration\b"
                r"|\b(?:configuration|environment)\s+(?:value|variable|setting)\s*[:=]",
                re.IGNORECASE,
            ),
        ),
        (
            DisclosureCategory.INFRASTRUCTURE,
            re.compile(
                r"\b(?:internal|private)\s+(?:endpoint|host|port|address)\b\s*[:=]"
                r"|\b(?:localhost|127\.0\.0\.1|10\.\d{1,3}\.\d{1,3}\.\d{1,3})\s*:\s*\d{2,5}\b",
                re.IGNORECASE,
            ),
        ),
        (
            DisclosureCategory.FILE_PATH,
            re.compile(
                r"(?:^|\s)/(?:home|srv|app|etc|var|tmp|workspace)/[^\s]+"
                r"|\b(?:backend|frontend)/(?:src|tests)/[^\s]+",
                re.IGNORECASE,
            ),
        ),
        (
            DisclosureCategory.SQL,
            re.compile(
                r"\b(?:select|insert|update|delete|drop|alter)\b.{0,120}\b(?:from|into|table|where)\b",
                re.IGNORECASE,
            ),
        ),
        (
            DisclosureCategory.STACK_TRACE,
            re.compile(
                r"\bTraceback \(most recent call last\):|\bFile \"[^\"]+\", line \d+",
                re.IGNORECASE,
            ),
        ),
        (
            DisclosureCategory.EXECUTION_INSTRUCTION,
            re.compile(
                r"(?:^|\n)\s*(?:sudo\s+|curl\s+https?://|wget\s+https?://|rm\s+-rf\s+|DROP\s+TABLE\b)"
                r"|\b(?:run|execute)\s+(?:this\s+)?(?:shell|terminal|sql|command|script)\b",
                re.IGNORECASE,
            ),
        ),
    )

    def assess(self, answer_text: str) -> DisclosureAssessment:
        categories = tuple(
            category for category, pattern in self._patterns if pattern.search(answer_text)
        )
        return DisclosureAssessment(safe=not categories, categories=categories)

    def validate(self, answer_text: str) -> str:
        """Return answer text or a generic safe replacement, never internal diagnostics."""

        return answer_text if self.assess(answer_text).safe else self.safe_replacement

    def is_safe(self, answer_text: str) -> bool:
        return self.assess(answer_text).safe
