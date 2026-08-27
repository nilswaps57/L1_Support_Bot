"""SQLAlchemy mapping for supervised answer feedback."""

from datetime import datetime

from sqlalchemy import JSON, Boolean, DateTime, Index, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from l1_support_bot.infrastructure.persistence.models.documents import Base


class FeedbackModel(Base):
    __tablename__ = "feedback"
    __table_args__ = (Index("ix_feedback_session_id", "session_id"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    answer_id: Mapped[str] = mapped_column(String(36), nullable=False, unique=True)
    session_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    question: Mapped[str] = mapped_column(Text, nullable=False)
    answer_text: Mapped[str] = mapped_column(Text, nullable=False)
    answer_type: Mapped[str] = mapped_column(String(20), nullable=False)
    rating: Mapped[str] = mapped_column(String(20), nullable=False)
    comment: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    llm_config_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    embedding_config_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    retrieval_config_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    retrieved_chunk_ids: Mapped[list[str]] = mapped_column(JSON, nullable=False)
    insufficient_information: Mapped[bool] = mapped_column(Boolean, nullable=False)
    submitted_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)