"""Conservative evidence gate for grounded answer generation."""

from __future__ import annotations

import re
from dataclasses import dataclass
from enum import StrEnum
from typing import Final

from l1_support_bot.domain.models.configuration import RetrievalConfig
from l1_support_bot.domain.ports.vector_store import VectorSearchResult


class EvidenceStatus(StrEnum):
    SUFFICIENT = "SUFFICIENT"
    INSUFFICIENT = "INSUFFICIENT"
    INCORRECT_PREMISE = "INCORRECT_PREMISE"


@dataclass(frozen=True, slots=True)
class EvidenceAssessment:
    status: EvidenceStatus
    results: tuple[VectorSearchResult, ...] = ()
    reason: str = ""


_WORD_PATTERN: Final = re.compile(r"[a-z0-9][a-z0-9_-]+", re.IGNORECASE)
_IDENTIFIER_PATTERN: Final = re.compile(r"\b[A-Z]{2,8}(?:-\d+|\d{3,})\b", re.IGNORECASE)
_STOP_WORDS: Final = frozenset(
    {
        "about",
        "does",
        "from",
        "have",
        "how",
        "what",
        "which",
        "where",
        "with",
        "would",
        "the",
        "this",
        "that",
        "its",
    }
)


class EvidenceSufficiencyPolicy:
    def __init__(self, config: RetrievalConfig | None = None) -> None:
        self.config = config or RetrievalConfig()

    def evaluate(
        self, question: str, results: tuple[VectorSearchResult, ...] | list[VectorSearchResult]
    ) -> EvidenceAssessment:
        candidates = tuple(results)
        if not candidates:
            return EvidenceAssessment(EvidenceStatus.INSUFFICIENT, reason="no_results")

        identifiers = self._identifiers(question)
        exact = tuple(result for result in candidates if self._has_identifier(result, identifiers))
        if identifiers and not exact:
            return EvidenceAssessment(
                EvidenceStatus.INCORRECT_PREMISE, reason="identifier_not_found"
            )

        scored = tuple(
            result for result in candidates if result.score >= self.config.similarity_threshold
        )
        if exact:
            scored = exact + tuple(result for result in scored if result not in exact)
        if not scored:
            return EvidenceAssessment(EvidenceStatus.INSUFFICIENT, reason="below_score_threshold")

        relevant = tuple(
            result for result in scored if result in exact or self._is_relevant(question, result)
        )
        if not relevant:
            return EvidenceAssessment(EvidenceStatus.INSUFFICIENT, reason="irrelevant_results")

        token_count = sum(self._token_count(result.chunk.text) for result in relevant)
        if not exact and token_count < self.config.min_evidence_tokens:
            return EvidenceAssessment(EvidenceStatus.INSUFFICIENT, reason="below_token_threshold")
        return EvidenceAssessment(EvidenceStatus.SUFFICIENT, relevant)

    @staticmethod
    def _identifiers(question: str) -> frozenset[str]:
        return frozenset(match.upper() for match in _IDENTIFIER_PATTERN.findall(question))

    @classmethod
    def _has_identifier(cls, result: VectorSearchResult, identifiers: frozenset[str]) -> bool:
        if not identifiers:
            return False
        metadata = result.chunk.metadata
        values = {
            value.upper()
            for value in (metadata.task_code, metadata.error_code, metadata.jira_id)
            if value
        }
        values.update(value.upper() for value in _IDENTIFIER_PATTERN.findall(result.chunk.text))
        return bool(identifiers & values)

    @classmethod
    def _is_relevant(cls, question: str, result: VectorSearchResult) -> bool:
        question_terms = {
            term.lower()
            for term in _WORD_PATTERN.findall(question)
            if term.lower() not in _STOP_WORDS and len(term) > 2
        }
        source = (
            result.chunk.text
            + " "
            + " ".join(
                value
                for value in (
                    result.chunk.metadata.document_name,
                    result.chunk.metadata.section,
                    result.chunk.metadata.task_code,
                    result.chunk.metadata.screen_name,
                    result.chunk.metadata.menu_path,
                    result.chunk.metadata.error_code,
                )
                if value
            )
        )
        source_terms = {term.lower() for term in _WORD_PATTERN.findall(source)}
        return bool(question_terms & source_terms)

    @staticmethod
    def _token_count(text: str) -> int:
        return len(_WORD_PATTERN.findall(text))
