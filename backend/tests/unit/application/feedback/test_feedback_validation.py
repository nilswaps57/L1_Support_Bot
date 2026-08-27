from datetime import UTC, datetime
from uuid import uuid4

import pytest

from l1_support_bot.domain.models.feedback import Feedback, FeedbackRating


def test_feedback_requires_answer_linkage_and_valid_rating() -> None:
    with pytest.raises(ValueError, match="answer"):
        Feedback.new(
            answer_id=None,
            session_id=uuid4(),
            question="What is BA435?",
            answer_text="It opens the account screen.",
            rating="helpful",
        )

    with pytest.raises(ValueError, match="rating"):
        Feedback.new(
            answer_id=uuid4(),
            session_id=uuid4(),
            question="What is BA435?",
            answer_text="It opens the account screen.",
            rating="maybe",
        )


def test_feedback_validates_comment_length_and_preserves_context() -> None:
    answer_id = uuid4()
    chunk_id = uuid4()
    feedback = Feedback.new(
        answer_id=answer_id,
        session_id=uuid4(),
        question="What is BA435?",
        answer_text="It opens the account screen.",
        answer_type="GROUNDED",
        rating=FeedbackRating.HELPFUL,
        comment="Clear answer",
        llm_config_id="llm-1",
        embedding_config_id="embedding-1",
        retrieval_config_id="retrieval-1",
        retrieved_chunk_ids=(chunk_id,),
        submitted_at=datetime(2026, 8, 27, tzinfo=UTC),
    )

    assert feedback.answer_id == answer_id
    assert feedback.retrieved_chunk_ids == (chunk_id,)
    assert feedback.submitted_at.year == 2026

    with pytest.raises(ValueError, match="1000"):
        Feedback.new(
            answer_id=answer_id,
            session_id=None,
            question="Question",
            answer_text="Answer",
            rating=FeedbackRating.NOT_HELPFUL,
            comment="x" * 1001,
        )


def test_feedback_has_no_system_update_capability() -> None:
    feedback = Feedback.new(
        answer_id=uuid4(),
        session_id=None,
        question="Question",
        answer_text="Answer",
        rating=FeedbackRating.NOT_HELPFUL,
    )

    assert not hasattr(feedback, "update_prompt")
    assert not hasattr(feedback, "update_retrieval")
    assert not hasattr(feedback, "update_knowledge_base")