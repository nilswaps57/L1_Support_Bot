"""Grounded answer value object."""

from dataclasses import dataclass, field
from enum import StrEnum
from uuid import UUID, uuid4

from l1_support_bot.domain.models.citation import Citation


class AnswerType(StrEnum):
    GROUNDED = "GROUNDED"
    PARTIAL = "PARTIAL"
    INSUFFICIENT = "INSUFFICIENT"
    AMBIGUOUS = "AMBIGUOUS"
    INCORRECT_PREMISE = "INCORRECT_PREMISE"


@dataclass(frozen=True, slots=True)
class Answer:
    question: str
    answer_text: str
    answer_type: AnswerType
    citations: tuple[Citation, ...] = ()
    insufficient_information: bool = False
    model_used: str | None = None
    llm_config_id: str | None = None
    embedding_config_id: str | None = None
    retrieval_config_id: str | None = None
    answer_id: UUID = field(default_factory=uuid4)

    @property
    def retrieved_chunk_ids(self) -> tuple[UUID, ...]:
        return tuple(citation.chunk_id for citation in self.citations)

    def __post_init__(self) -> None:
        if not self.question.strip() or not self.answer_text.strip():
            raise ValueError("Answer question and text cannot be empty")
        if self.answer_type in {AnswerType.GROUNDED, AnswerType.PARTIAL} and not self.citations:
            raise ValueError("Grounded and partial answers require supporting citations")
        if (
            self.answer_type
            in {AnswerType.INSUFFICIENT, AnswerType.AMBIGUOUS, AnswerType.INCORRECT_PREMISE}
            and self.citations
        ):
            raise ValueError("Non-supported answers cannot contain citations")
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
