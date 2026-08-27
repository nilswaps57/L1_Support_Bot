"""Capture supervised feedback without changing chatbot behavior."""

from uuid import UUID

from l1_support_bot.domain.models.answer import Answer
from l1_support_bot.domain.models.feedback import Feedback, FeedbackRating
from l1_support_bot.domain.ports.feedback_repository import FeedbackRepository


class SubmitFeedback:
    def __init__(self, repository: FeedbackRepository) -> None:
        self.repository = repository

    async def execute(
        self,
        *,
        answer: Answer,
        session_id: UUID | None,
        rating: FeedbackRating | str,
        comment: str | None = None,
    ) -> Feedback:
        existing = await self.repository.get_by_answer(answer.answer_id)
        if existing is not None:
            return existing
        feedback = Feedback.new(
            answer_id=answer.answer_id,
            session_id=session_id,
            question=answer.question,
            answer_text=answer.answer_text,
            answer_type=answer.answer_type.value,
            rating=rating,
            comment=comment,
            llm_config_id=answer.llm_config_id,
            embedding_config_id=answer.embedding_config_id,
            retrieval_config_id=answer.retrieval_config_id,
            retrieved_chunk_ids=answer.retrieved_chunk_ids,
            insufficient_information=answer.insufficient_information,
        )
        return await self.repository.save(feedback)