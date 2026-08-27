"""Add non-secret LLM and chunking configuration tables."""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "006_ai_rag_configuration"
down_revision: str | None = "006_feedback"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "llm_configurations",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("provider", sa.String(length=50), nullable=False),
        sa.Column("model", sa.String(length=200), nullable=False),
        sa.Column("endpoint", sa.String(length=500), nullable=False),
        sa.Column("temperature", sa.Float(), nullable=False),
        sa.Column("max_tokens", sa.Integer(), nullable=False),
        sa.Column("context_window", sa.Integer(), nullable=False),
        sa.Column("timeout_seconds", sa.Integer(), nullable=False),
        sa.Column("max_retries", sa.Integer(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("label", sa.String(length=200), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_llm_configurations_active", "llm_configurations", ["is_active", "updated_at"]
    )
    op.create_table(
        "chunking_configurations",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("strategy", sa.String(length=50), nullable=False),
        sa.Column("target_chunk_tokens", sa.Integer(), nullable=False),
        sa.Column("min_chunk_tokens", sa.Integer(), nullable=False),
        sa.Column("max_chunk_tokens", sa.Integer(), nullable=False),
        sa.Column("overlap_tokens", sa.Integer(), nullable=False),
        sa.Column("table_as_unit", sa.Boolean(), nullable=False),
        sa.Column("procedure_grouping", sa.Boolean(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_chunking_configurations_active",
        "chunking_configurations",
        ["is_active", "updated_at"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_chunking_configurations_active", table_name="chunking_configurations"
    )
    op.drop_table("chunking_configurations")
    op.drop_index("ix_llm_configurations_active", table_name="llm_configurations")
    op.drop_table("llm_configurations")