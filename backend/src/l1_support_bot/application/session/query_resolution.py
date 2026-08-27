"""Resolve conversational references without treating history as evidence."""

import re
from collections.abc import Sequence
from dataclasses import dataclass

from l1_support_bot.domain.models.session import ChatMessage

_IDENTIFIER = re.compile(r"\b[A-Z]{2,5}\d{2,}\b")
_SCREEN = re.compile(
    r"\b((?:[A-Z][A-Za-z0-9]+\s+){0,4}[A-Z][A-Za-z0-9]+)\s+(?i:screen)\b",
)
_REFERENCE = re.compile(
    r"\b(?:it|its|that screen|the previous task code|previous task code)\b", re.I
)


@dataclass(frozen=True, slots=True)
class ResolvedQuery:
    original_query: str
    retrieval_query: str
    history: tuple[ChatMessage, ...]
    is_follow_up: bool
    ambiguous: bool = False


class QueryResolution:
    def __init__(self, *, history_window_turns: int = 10, token_budget: int = 2_000) -> None:
        if history_window_turns < 1 or token_budget < 1:
            raise ValueError("Query-resolution limits must be positive")
        self.history_window_turns = history_window_turns
        self.token_budget = token_budget

    @staticmethod
    def estimate_tokens(content: str) -> int:
        return max(1, len(content.split()))

    def select_history(self, history: Sequence[ChatMessage]) -> tuple[ChatMessage, ...]:
        messages = tuple(history)
        turns = [messages[index : index + 2] for index in range(0, len(messages), 2)]
        selected: list[ChatMessage] = []
        used_tokens = 0
        for turn in reversed(turns[-self.history_window_turns :]):
            turn_tokens = sum(self.estimate_tokens(item.content) for item in turn)
            if used_tokens + turn_tokens > self.token_budget:
                continue
            selected[0:0] = list(turn)
            used_tokens += turn_tokens
        return tuple(selected)

    def resolve(
        self,
        question: str,
        history: Sequence[ChatMessage],
    ) -> ResolvedQuery:
        bounded_history = self.select_history(history)
        if not bounded_history or not _REFERENCE.search(question):
            return ResolvedQuery(question, question, bounded_history, False)

        text = "\n".join(message.content for message in bounded_history)
        identifiers = list(dict.fromkeys(_IDENTIFIER.findall(text)))
        screens = [
            f"{match.group(1).strip()} screen"
            for match in _SCREEN.finditer(text)
            if match.group(1).strip()
        ]
        screens = list(dict.fromkeys(screen.removeprefix("The ") for screen in screens))
        reference = question.lower()
        uses_task_reference = "task code" in reference or bool(
            re.search(r"\b(?:it|its)\b", reference)
        )
        ambiguous = (uses_task_reference and len(identifiers) > 1) or (
            "screen" in reference and not identifiers and len(screens) > 1
        )
        if ambiguous or (not identifiers and not screens):
            return ResolvedQuery(question, question, bounded_history, True, ambiguous)

        topic = identifiers[-1] if identifiers else screens[-1]
        if "screen" in reference and not identifiers:
            topic = screens[-1]
        rewritten = re.sub(
            r"\bthe previous task code\b|\bprevious task code\b",
            topic,
            question,
            flags=re.IGNORECASE,
        )
        rewritten = re.sub(r"\bits?\b", topic, rewritten, flags=re.IGNORECASE)
        if "screen" in reference and screens:
            rewritten = re.sub(r"\bthat screen\b", topic, rewritten, flags=re.IGNORECASE)
        return ResolvedQuery(question, rewritten, bounded_history, True)