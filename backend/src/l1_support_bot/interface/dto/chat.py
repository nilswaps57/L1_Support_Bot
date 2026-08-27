"""Minimal Phase 5 grounded-chat API schemas."""

from uuid import UUID

from pydantic import BaseModel, Field

from l1_support_bot.domain.models.answer import Answer


class ChatRequest(BaseModel):
    session_id: UUID
    question: str


class ChatCitation(BaseModel):
    chunk_id: UUID
    document_id: UUID
    document_name: str
    page_number: int | None = None
    section: str | None = None
    task_code: str | None = None
    screen_name: str | None = None
    source_type: str | None = None
    error_code: str | None = None
    jira_id: str | None = None
    relevance_score: float | None = None


class ChatResponse(BaseModel):
    session_id: UUID
    question: str
    answer_text: str
    answer_type: str
    citations: list[ChatCitation] = Field(default_factory=list)
    insufficient_information: bool
    model_used: str | None = None

    @classmethod
    def from_answer(cls, session_id: UUID, answer: Answer) -> "ChatResponse":
        return cls(
            session_id=session_id,
            question=answer.question,
            answer_text=answer.answer_text,
            answer_type=answer.answer_type.value,
            citations=[
                ChatCitation.model_validate(citation, from_attributes=True)
                for citation in answer.citations
            ],
            insufficient_information=answer.insufficient_information,
            model_used=answer.model_used,
        )
