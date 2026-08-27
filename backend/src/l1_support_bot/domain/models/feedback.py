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
    answer_id: UUID
    session_id: UUID | None
    question: str
    answer_text: str
    answer_type: str
    rating: FeedbackRating
    comment: str | None
    llm_config_id: str | None
    embedding_config_id: str | None
    retrieval_config_id: str | None
    retrieved_chunk_ids: tuple[UUID, ...]
    insufficient_information: bool
    submitted_at: datetime

    def __post_init__(self) -> None:
        if not self.answer_id:
            raise ValueError("Feedback must link to an answer")
        if not self.question.strip() or not self.answer_text.strip():
            raise ValueError("Feedback must link to a question and answer")
        if not isinstance(self.rating, FeedbackRating):
            raise ValueError("Feedback rating must be helpful or not_helpful")
        if self.comment is not None and len(self.comment) > 1000:
            raise ValueError("Feedback comment cannot exceed 1000 characters")

    @classmethod
    def new(
        cls,
        *,
        answer_id: UUID | None,
        session_id: UUID | None,
        question: str,
        answer_text: str,
        rating: FeedbackRating | str,
        answer_type: str = "GROUNDED",
        comment: str | None = None,
        llm_config_id: str | None = None,
        embedding_config_id: str | None = None,
        retrieval_config_id: str | None = None,
        retrieved_chunk_ids: tuple[UUID, ...] = (),
        insufficient_information: bool = False,
        submitted_at: datetime | None = None,
    ) -> "Feedback":
        if answer_id is None:
            raise ValueError("Feedback must link to an answer")
        try:
            resolved_rating = FeedbackRating(rating)
        except ValueError as exc:
            raise ValueError("Feedback rating must be helpful or not_helpful") from exc
        return cls(
            id=uuid4(),
            answer_id=answer_id,
            session_id=session_id,
            question=question,
            answer_text=answer_text,
            answer_type=answer_type,
            rating=resolved_rating,
            comment=comment,
            llm_config_id=llm_config_id,
            embedding_config_id=embedding_config_id,
            retrieval_config_id=retrieval_config_id,
            retrieved_chunk_ids=tuple(retrieved_chunk_ids),
            insufficient_information=insufficient_information,
            submitted_at=submitted_at or datetime.now(UTC),
        )