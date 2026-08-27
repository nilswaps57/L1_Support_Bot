"""Public feedback request and response schemas."""

from uuid import UUID

from pydantic import BaseModel, Field

from l1_support_bot.domain.models.feedback import FeedbackRating


class FeedbackRequest(BaseModel):
    session_id: UUID
    answer_id: UUID
    rating: FeedbackRating
    comment: str | None = Field(default=None, max_length=1000)


class FeedbackResponse(BaseModel):
    feedback_id: UUID