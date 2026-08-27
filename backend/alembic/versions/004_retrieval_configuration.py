"""Persist hybrid retrieval configuration."""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "004_retrieval_configuration"
down_revision: str | None = "003_embedding_configuration"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "retrieval_configurations",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("top_k_candidates", sa.Integer(), nullable=False),
        sa.Column("final_top_k", sa.Integer(), nullable=False),
        sa.Column("similarity_threshold", sa.Float(), nullable=False),
        sa.Column("dense_weight", sa.Float(), nullable=False),
        sa.Column("sparse_weight", sa.Float(), nullable=False),
        sa.Column("rerank_enabled", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("rerank_top_k", sa.Integer(), nullable=False),
        sa.Column("exact_id_boost", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("min_evidence_tokens", sa.Integer(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_retrieval_configurations_active",
        "retrieval_configurations",
        ["is_active", "updated_at"],
    )


def downgrade() -> None:
    op.drop_index("ix_retrieval_configurations_active", table_name="retrieval_configurations")
    op.drop_table("retrieval_configurations")
