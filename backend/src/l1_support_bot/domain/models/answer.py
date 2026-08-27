"""Grounded answer value object."""

from dataclasses import dataclass
from enum import StrEnum

from l1_support_bot.domain.models.citation import Citation


class AnswerType(StrEnum):
    GROUNDED = "GROUNDED"
    PARTIAL = "PARTIAL"
    INSUFFICIENT = "INSUFFICIENT"
    AMBIGUOUS = "AMBIGUOUS"


@dataclass(frozen=True, slots=True)
class Answer:
    question: str
    answer_text: str
    answer_type: AnswerType
    citations: tuple[Citation, ...] = ()
    insufficient_information: bool = False
    model_used: str | None = None

    def __post_init__(self) -> None:
        if not self.question.strip() or not self.answer_text.strip():
            raise ValueError("Answer question and text cannot be empty")
        if self.answer_type in {AnswerType.GROUNDED, AnswerType.PARTIAL} and not self.citations:
            raise ValueError("Grounded and partial answers require supporting citations")
        if self.answer_type is AnswerType.INSUFFICIENT and self.citations:
            raise ValueError("Insufficient answers cannot contain citations")
        if self.insufficient_information != (self.answer_type is AnswerType.INSUFFICIENT):
            raise ValueError("Insufficient-information flag must match answer type")

    @classmethod
    def insufficient(cls, answer_text: str) -> "Answer":
        return cls(
            question="Unavailable question",
            answer_text=answer_text,
            answer_type=AnswerType.INSUFFICIENT,
            insufficient_information=True,
        )