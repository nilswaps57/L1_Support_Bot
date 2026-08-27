"""Feedback domain value."""

from dataclasses import dataclass
from datetime import UTC, datetime
from enum import StrEnum
from uuid import UUID, uuid4


class FeedbackRating(StrEnum):
    HELPFUL = "helpful"
    NOT_HELPFUL = "not_helpful"


@dataclass(frozen=True, slots=True)
class Feedback:
    id: UUID
    session_id: UUID | None
    question: str
    answer_text: str
    rating: FeedbackRating
    comment: str | None
    submitted_at: datetime

    def __post_init__(self) -> None:
        if not self.question.strip() or not self.answer_text.strip():
            raise ValueError("Feedback must link to a question and answer")
        if self.comment is not None and len(self.comment) > 1000:
            raise ValueError("Feedback comment cannot exceed 1000 characters")

    @classmethod
    def new(
        cls,
        *,
        session_id: UUID | None,
        question: str,
        answer_text: str,
        rating: FeedbackRating,
        comment: str | None = None,
    ) -> "Feedback":
        return cls(uuid4(), session_id, question, answer_text, rating, comment, datetime.now(UTC))