"""Persist prepared knowledge chunks and ingestion diagnostics."""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "002_chunks_and_ingestion_diagnostics"
down_revision: str | None = "001_documents_and_jobs"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "knowledge_chunks",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("document_id", sa.String(length=36), nullable=False),
        sa.Column("ingestion_job_id", sa.String(length=36), nullable=False),
        sa.Column("chunk_seq", sa.Integer(), nullable=False),
        sa.Column("text_preview", sa.String(length=500), nullable=False),
        sa.Column("text", sa.Text(), nullable=False),
        sa.Column("page_number", sa.Integer(), nullable=True),
        sa.Column("section_path", sa.String(length=1000), nullable=True),
        sa.Column("task_code", sa.String(length=20), nullable=True),
        sa.Column("screen_name", sa.String(length=200), nullable=True),
        sa.Column("module", sa.String(length=100), nullable=True),
        sa.Column("functional_area", sa.String(length=200), nullable=True),
        sa.Column("menu_path", sa.String(length=500), nullable=True),
        sa.Column("prerequisites", sa.JSON(), nullable=False),
        sa.Column("modes", sa.JSON(), nullable=False),
        sa.Column("field_names", sa.JSON(), nullable=False),
        sa.Column("procedure_steps", sa.JSON(), nullable=False),
        sa.Column("error_code", sa.String(length=50), nullable=True),
        sa.Column("jira_id", sa.String(length=50), nullable=True),
        sa.Column("rca_reference", sa.String(length=100), nullable=True),
        sa.Column("element_type", sa.String(length=30), nullable=False),
        sa.Column("embedding_model_id", sa.String(length=200), nullable=True),
        sa.Column("indexed_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["document_id"], ["documents.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["ingestion_job_id"], ["ingestion_jobs.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_knowledge_chunks_document_id", "knowledge_chunks", ["document_id"])
    op.create_index("ix_knowledge_chunks_task_code", "knowledge_chunks", ["task_code"])
    op.create_index("ix_knowledge_chunks_error_code", "knowledge_chunks", ["error_code"])
    op.create_table(
        "ingestion_diagnostics",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("ingestion_job_id", sa.String(length=36), nullable=False),
        sa.Column("element_type", sa.String(length=30), nullable=False),
        sa.Column("code", sa.String(length=50), nullable=True),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("page_number", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["ingestion_job_id"], ["ingestion_jobs.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_ingestion_diagnostics_job_id",
        "ingestion_diagnostics",
        ["ingestion_job_id"],
    )


def downgrade() -> None:
    op.drop_index("ix_ingestion_diagnostics_job_id", table_name="ingestion_diagnostics")
    op.drop_table("ingestion_diagnostics")
    op.drop_index("ix_knowledge_chunks_error_code", table_name="knowledge_chunks")
    op.drop_index("ix_knowledge_chunks_task_code", table_name="knowledge_chunks")
    op.drop_index("ix_knowledge_chunks_document_id", table_name="knowledge_chunks")
    op.drop_table("knowledge_chunks")
