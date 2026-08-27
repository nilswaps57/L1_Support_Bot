"""SQLAlchemy mapping for retrieval configuration."""

from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, Index, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from l1_support_bot.infrastructure.persistence.models.documents import Base


class RetrievalConfigurationModel(Base):
    __tablename__ = "retrieval_configurations"
    __table_args__ = (Index("ix_retrieval_configurations_active", "is_active", "updated_at"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    top_k_candidates: Mapped[int] = mapped_column(Integer, nullable=False)
    final_top_k: Mapped[int] = mapped_column(Integer, nullable=False)
    similarity_threshold: Mapped[float] = mapped_column(Float, nullable=False)
    dense_weight: Mapped[float] = mapped_column(Float, nullable=False)
    sparse_weight: Mapped[float] = mapped_column(Float, nullable=False)
    rerank_enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    rerank_top_k: Mapped[int] = mapped_column(Integer, nullable=False)
    exact_id_boost: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    min_evidence_tokens: Mapped[int] = mapped_column(Integer, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
