"""SQLAlchemy mapping for non-secret LLM configuration."""

from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, Index, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from l1_support_bot.infrastructure.persistence.models.documents import Base


class LLMConfigurationModel(Base):
    __tablename__ = "llm_configurations"
    __table_args__ = (Index("ix_llm_configurations_active", "is_active", "updated_at"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    provider: Mapped[str] = mapped_column(String(50), nullable=False)
    model: Mapped[str] = mapped_column(String(200), nullable=False)
    endpoint: Mapped[str] = mapped_column(String(500), nullable=False)
    temperature: Mapped[float] = mapped_column(Float, nullable=False)
    max_tokens: Mapped[int] = mapped_column(Integer, nullable=False)
    context_window: Mapped[int] = mapped_column(Integer, nullable=False)
    timeout_seconds: Mapped[int] = mapped_column(Integer, nullable=False)
    max_retries: Mapped[int] = mapped_column(Integer, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    label: Mapped[str | None] = mapped_column(String(200), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class ChunkingConfigurationModel(Base):
    __tablename__ = "chunking_configurations"
    __table_args__ = (
        Index("ix_chunking_configurations_active", "is_active", "updated_at"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    strategy: Mapped[str] = mapped_column(String(50), nullable=False)
    target_chunk_tokens: Mapped[int] = mapped_column(Integer, nullable=False)
    min_chunk_tokens: Mapped[int] = mapped_column(Integer, nullable=False)
    max_chunk_tokens: Mapped[int] = mapped_column(Integer, nullable=False)
    overlap_tokens: Mapped[int] = mapped_column(Integer, nullable=False)
    table_as_unit: Mapped[bool] = mapped_column(Boolean, nullable=False)
    procedure_grouping: Mapped[bool] = mapped_column(Boolean, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)