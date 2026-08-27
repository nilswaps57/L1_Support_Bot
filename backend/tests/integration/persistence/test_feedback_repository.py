from datetime import UTC, datetime
from uuid import uuid4

import pytest
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from l1_support_bot.domain.models.feedback import Feedback, FeedbackRating
from l1_support_bot.infrastructure.persistence.models import Base
from l1_support_bot.infrastructure.persistence.sqlalchemy.feedback_repository import (
    SqlAlchemyFeedbackRepository,
)


@pytest.mark.integration
async def test_feedback_repository_round_trips_answer_context() -> None:
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)

    repository = SqlAlchemyFeedbackRepository(async_sessionmaker(engine, expire_on_commit=False))
    feedback = Feedback.new(
        answer_id=uuid4(),
        session_id=uuid4(),
        question="What is BA435?",
        answer_text="It opens the account screen.",
        answer_type="GROUNDED",
        rating=FeedbackRating.HELPFUL,
        comment="Useful",
        llm_config_id="llm-1",
        embedding_config_id="embedding-1",
        retrieval_config_id="retrieval-1",
        retrieved_chunk_ids=(uuid4(), uuid4()),
        submitted_at=datetime(2026, 8, 27, tzinfo=UTC),
    )

    saved = await repository.save(feedback)
    rows = await repository.list_by_answer(feedback.answer_id)

    assert saved == feedback
    assert rows == (feedback,)
    await engine.dispose()