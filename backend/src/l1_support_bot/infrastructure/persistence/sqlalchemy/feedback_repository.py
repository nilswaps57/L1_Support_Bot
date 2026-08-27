"""SQLAlchemy repository for supervised answer feedback."""

from collections.abc import Sequence
from datetime import UTC
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from l1_support_bot.domain.models.feedback import Feedback, FeedbackRating
from l1_support_bot.infrastructure.persistence.models.feedback import FeedbackModel


class SqlAlchemyFeedbackRepository:
    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        self.session_factory = session_factory

    async def save(self, feedback: Feedback) -> Feedback:
        model = _to_model(feedback)
        async with self.session_factory() as session:
            session.add(model)
            try:
                await session.commit()
            except IntegrityError:
                await session.rollback()
                existing = await self._get(session, feedback.answer_id)
                if existing is None:
                    raise
                return existing
        return feedback

    async def get_by_answer(self, answer_id: UUID) -> Feedback | None:
        async with self.session_factory() as session:
            return await self._get(session, answer_id)

    async def list_by_answer(self, answer_id: UUID) -> Sequence[Feedback]:
        item = await self.get_by_answer(answer_id)
        return () if item is None else (item,)

    async def list_by_session(self, session_id: UUID) -> Sequence[Feedback]:
        async with self.session_factory() as session:
            result = await session.scalars(
                select(FeedbackModel).where(FeedbackModel.session_id == str(session_id))
            )
            return tuple(_to_domain(model) for model in result)

    async def _get(self, session: AsyncSession, answer_id: UUID) -> Feedback | None:
        model = await session.scalar(
            select(FeedbackModel).where(FeedbackModel.answer_id == str(answer_id))
        )
        return None if model is None else _to_domain(model)


def _to_model(feedback: Feedback) -> FeedbackModel:
    return FeedbackModel(
        id=str(feedback.id),
        answer_id=str(feedback.answer_id),
        session_id=str(feedback.session_id) if feedback.session_id else None,
        question=feedback.question,
        answer_text=feedback.answer_text,
        answer_type=feedback.answer_type,
        rating=feedback.rating.value,
        comment=feedback.comment,
        llm_config_id=feedback.llm_config_id,
        embedding_config_id=feedback.embedding_config_id,
        retrieval_config_id=feedback.retrieval_config_id,
        retrieved_chunk_ids=[str(item) for item in feedback.retrieved_chunk_ids],
        insufficient_information=feedback.insufficient_information,
        submitted_at=feedback.submitted_at,
    )


def _to_domain(model: FeedbackModel) -> Feedback:
    submitted_at = model.submitted_at
    if submitted_at.tzinfo is None:
        submitted_at = submitted_at.replace(tzinfo=UTC)
    return Feedback(
        id=UUID(model.id),
        answer_id=UUID(model.answer_id),
        session_id=UUID(model.session_id) if model.session_id else None,
        question=model.question,
        answer_text=model.answer_text,
        answer_type=model.answer_type,
        rating=FeedbackRating(model.rating),
        comment=model.comment,
        llm_config_id=model.llm_config_id,
        embedding_config_id=model.embedding_config_id,
        retrieval_config_id=model.retrieval_config_id,
        retrieved_chunk_ids=tuple(UUID(item) for item in (model.retrieved_chunk_ids or [])),
        insufficient_information=model.insufficient_information,
        submitted_at=submitted_at,
    )