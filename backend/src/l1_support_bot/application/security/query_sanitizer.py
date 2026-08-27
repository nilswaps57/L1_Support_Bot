"""Classify prompt-injection attempts without rewriting user intent."""

from __future__ import annotations

import base64
import binascii
import html
import re
import unicodedata
from dataclasses import dataclass
from enum import StrEnum
from urllib.parse import unquote


class InjectionCategory(StrEnum):
    """Safe, aggregate categories suitable for privacy-preserving logs."""

    INSTRUCTION_OVERRIDE = "instruction_override"
    ROLE_CONFUSION = "role_confusion"
    PROMPT_DISCLOSURE = "prompt_disclosure"
    CONFIGURATION_DISCLOSURE = "configuration_disclosure"
    COMMAND_EXECUTION = "command_execution"
    GENERAL_KNOWLEDGE_BYPASS = "general_knowledge_bypass"
    FABRICATED_CITATION = "fabricated_citation"
    ENCODED_INSTRUCTION = "encoded_instruction"


@dataclass(frozen=True, slots=True)
class QuerySecurityAssessment:
    """Classification metadata; neither field contains a rewritten user prompt."""

    normalized_query: str
    categories: tuple[InjectionCategory, ...] = ()
    has_domain_signal: bool = False

    @property
    def contains_injection(self) -> bool:
        return bool(self.categories)

    @property
    def should_refuse(self) -> bool:
        return self.contains_injection and not self.has_domain_signal


class QuerySanitizer:
    """Bound and normalize retrieval input while classifying control-plane language."""

    max_query_length = 8_000
    _zero_width = re.compile(
        r"[\u00ad\u034f\u061c\u180e\u200b-\u200f\u202a-\u202e\u2060\u2066-\u206f\ufeff]"
    )
    _override = re.compile(
        r"\b(?:ignore|disregard|forget|bypass|override)\b.{0,80}\b(?:previous|prior|above|earlier|system|developer|all)\b"
        r"|\b(?:previous|prior|above|earlier)\s+instructions?\b",
        re.IGNORECASE,
    )
    _role_confusion = re.compile(
        r"\b(?:you are now|act as|pretend to be|assume the role|developer message|"
        r"system message|assistant message)\b"
        r"|(?:^|\n)\s*(?:system|developer|assistant)\s*:\s*",
        re.IGNORECASE,
    )
    _prompt_disclosure = re.compile(
        r"\b(?:reveal|show|print|display|disclose|dump|repeat|quote|provide|expose)\b"
        r".{0,100}\b(?:system|developer|hidden|original)\s+(?:prompt|instructions?)\b"
        r"|\bwhat\s+(?:are|is)\s+(?:your|the)\s+(?:system|hidden|developer)\s+(?:prompt|instructions?)\b",
        re.IGNORECASE,
    )
    _configuration_disclosure = re.compile(
        r"\b(?:reveal|show|print|display|dump|expose|provide|leak|give me)\b"
        r".{0,100}\b(?:secrets?|credentials?|passwords?|api\s*keys?|tokens?|"
        r"environment variables?|internal endpoints?|configuration values?)\b"
        r"|\b(?:dump|print|show|reveal)\s+(?:the\s+)?(?:app(?:lication)\s+)?config(?:uration)?\b",
        re.IGNORECASE,
    )
    _command_execution = re.compile(
        r"\b(?:run|execute|invoke|launch|call)\b.{0,100}\b(?:shell|command|script|sql|query|curl|wget|bash|terminal|macro|transaction|mutation)\b"
        r"|\b(?:sudo|rm\s+-rf|curl\s+https?://|drop\s+table|delete\s+from)\b",
        re.IGNORECASE,
    )
    _general_knowledge = re.compile(
        r"\b(?:answer|respond|tell me)\b.{0,100}\b(?:from|using)\s+"
        r"(?:general|prior|pretrained|outside)\s+(?:knowledge|memory)\b"
        r"|\bwithout\s+(?:citations?|the\s+knowledge\s+base|retrieved\s+evidence)\b"
        r"|\bignore\s+(?:the\s+)?knowledge\s+base\b",
        re.IGNORECASE,
    )
    _fabricated_citation = re.compile(
        r"\b(?:fabricate|invent|fake|make\s+up|create)\b.{0,80}\b(?:citation|source|reference)\b",
        re.IGNORECASE,
    )
    _domain_signal = re.compile(
        r"\b(?:flexcube|task\s*code|screen|menu\s+path|prerequisite|field|procedure|error\s+code|jira|rca)\b"
        r"|\b[A-Z]{2,5}\d{3,5}\b|\b(?:ERR(?:OR)?[- ]?\d{2,6}|E[- ]?\d{2,6})\b",
        re.IGNORECASE,
    )

    def normalize(self, query: str) -> str:
        """Normalize only representation noise; never delete semantic query content."""

        normalized = unicodedata.normalize("NFKC", query)
        normalized = self._zero_width.sub("", normalized)
        normalized = " ".join(normalized.split())
        if not normalized:
            raise ValueError("Question cannot be empty.")
        if len(normalized) > self.max_query_length:
            raise ValueError("Question exceeds the permitted length.")
        return normalized

    def normalize_for_retrieval(self, query: str) -> str:
        """Expose retrieval normalization separately from injection classification."""

        return self.normalize(query)

    def assess(self, query: str) -> QuerySecurityAssessment:
        normalized = self.normalize(query)
        detection_text = self._detection_text(normalized)
        categories: list[InjectionCategory] = []
        checks = (
            (InjectionCategory.INSTRUCTION_OVERRIDE, self._override),
            (InjectionCategory.ROLE_CONFUSION, self._role_confusion),
            (InjectionCategory.PROMPT_DISCLOSURE, self._prompt_disclosure),
            (InjectionCategory.CONFIGURATION_DISCLOSURE, self._configuration_disclosure),
            (InjectionCategory.COMMAND_EXECUTION, self._command_execution),
            (InjectionCategory.GENERAL_KNOWLEDGE_BYPASS, self._general_knowledge),
            (InjectionCategory.FABRICATED_CITATION, self._fabricated_citation),
        )
        for category, pattern in checks:
            if pattern.search(detection_text):
                categories.append(category)
        if self._contains_encoded_instruction(normalized):
            categories.append(InjectionCategory.ENCODED_INSTRUCTION)
        return QuerySecurityAssessment(
            normalized_query=normalized,
            categories=tuple(categories),
            has_domain_signal=bool(self._domain_signal.search(normalized)),
        )

    @classmethod
    def _detection_text(cls, query: str) -> str:
        decoded = html.unescape(unquote(query))
        return cls._zero_width.sub("", decoded)

    @staticmethod
    def _contains_encoded_instruction(query: str) -> bool:
        candidates = re.findall(r"(?<![A-Za-z0-9])[A-Za-z0-9+/]{24,}={0,2}(?![A-Za-z0-9])", query)
        for candidate in candidates:
            try:
                decoded = base64.b64decode(candidate, validate=True).decode("utf-8")
            except (ValueError, UnicodeDecodeError, binascii.Error):
                continue
            folded = re.sub(r"\W+", "", decoded).lower()
            if (
                "ignorepreviousinstructions" in folded
                or "revealsystemprompt" in folded
                or "runcommand" in folded
            ):
                return True
        return False


def normalize_query(query: str) -> str:
    """Convenience wrapper for representation normalization."""

    return QuerySanitizer().normalize_for_retrieval(query)


def classify_query(query: str) -> QuerySecurityAssessment:
    """Convenience wrapper for security classification."""

    return QuerySanitizer().assess(query)


QueryInjectionClassifier = QuerySanitizer
