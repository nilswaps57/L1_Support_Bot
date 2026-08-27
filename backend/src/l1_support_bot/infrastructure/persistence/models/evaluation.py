"""SQLAlchemy mapping for reproducible RAG evaluation runs."""

from datetime import datetime

from sqlalchemy import JSON, DateTime, Index, String
from sqlalchemy.orm import Mapped, mapped_column

from l1_support_bot.infrastructure.persistence.models.documents import Base


class EvaluationRunModel(Base):
    __tablename__ = "evaluation_runs"
    __table_args__ = (Index("ix_evaluation_runs_dataset_id", "dataset_id"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    dataset_id: Mapped[str] = mapped_column(String(200), nullable=False)
    configuration_snapshot: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False)
    retrieval_metrics: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False)
    generation_metrics: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
