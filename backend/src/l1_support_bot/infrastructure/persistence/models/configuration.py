"""SQLAlchemy mappings for runtime AI configuration."""

from datetime import datetime

from sqlalchemy import Boolean, DateTime, Index, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from l1_support_bot.infrastructure.persistence.models.documents import Base


class EmbeddingConfigurationModel(Base):
    __tablename__ = "embedding_configurations"
    __table_args__ = (
        Index("ix_embedding_configurations_active", "is_active", "updated_at"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    provider: Mapped[str] = mapped_column(String(50), nullable=False)
    model: Mapped[str] = mapped_column(String(200), nullable=False)
    model_version: Mapped[str] = mapped_column(String(100), nullable=False)
    endpoint: Mapped[str] = mapped_column(String(500), nullable=False)
    dimensions: Mapped[int] = mapped_column(Integer, nullable=False)
    distance_method: Mapped[str] = mapped_column(String(20), nullable=False)
    index_compat_id: Mapped[str] = mapped_column(String(300), nullable=False)
    batch_size: Mapped[int] = mapped_column(Integer, nullable=False)
    timeout_seconds: Mapped[int] = mapped_column(Integer, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    label: Mapped[str | None] = mapped_column(String(200), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
