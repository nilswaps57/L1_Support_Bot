"""SQLAlchemy mappings for prepared knowledge chunks and diagnostics."""

from datetime import datetime

from sqlalchemy import JSON, DateTime, ForeignKey, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from l1_support_bot.infrastructure.persistence.models.documents import Base


class KnowledgeChunkModel(Base):
    __tablename__ = "knowledge_chunks"
    __table_args__ = (
        Index("ix_knowledge_chunks_document_id", "document_id"),
        Index("ix_knowledge_chunks_task_code", "task_code"),
        Index("ix_knowledge_chunks_error_code", "error_code"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    document_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("documents.id", ondelete="CASCADE"), nullable=False
    )
    ingestion_job_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("ingestion_jobs.id", ondelete="CASCADE"), nullable=False
    )
    chunk_seq: Mapped[int] = mapped_column(Integer, nullable=False)
    text_preview: Mapped[str] = mapped_column(String(500), nullable=False)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    source_type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    page_number: Mapped[int | None] = mapped_column(Integer, nullable=True)
    section_path: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    task_code: Mapped[str | None] = mapped_column(String(20), nullable=True)
    screen_name: Mapped[str | None] = mapped_column(String(200), nullable=True)
    module: Mapped[str | None] = mapped_column(String(100), nullable=True)
    functional_area: Mapped[str | None] = mapped_column(String(200), nullable=True)
    menu_path: Mapped[str | None] = mapped_column(String(500), nullable=True)
    prerequisites: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    modes: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    field_names: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    procedure_steps: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    error_code: Mapped[str | None] = mapped_column(String(50), nullable=True)
    jira_id: Mapped[str | None] = mapped_column(String(50), nullable=True)
    rca_reference: Mapped[str | None] = mapped_column(String(100), nullable=True)
    element_type: Mapped[str] = mapped_column(String(30), nullable=False)
    embedding_model_id: Mapped[str | None] = mapped_column(String(200), nullable=True)
    indexed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class IngestionDiagnosticModel(Base):
    __tablename__ = "ingestion_diagnostics"
    __table_args__ = (Index("ix_ingestion_diagnostics_job_id", "ingestion_job_id"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    ingestion_job_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("ingestion_jobs.id", ondelete="CASCADE"), nullable=False
    )
    element_type: Mapped[str] = mapped_column(String(30), nullable=False)
    code: Mapped[str | None] = mapped_column(String(50), nullable=True)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    page_number: Mapped[int | None] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
