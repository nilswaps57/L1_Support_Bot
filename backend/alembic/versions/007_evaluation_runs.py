"""Persist reproducible RAG evaluation runs."""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "007_evaluation_runs"
down_revision: str | None = "006_ai_rag_configuration"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "evaluation_runs",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("dataset_id", sa.String(length=200), nullable=False),
        sa.Column("configuration_snapshot", sa.JSON(), nullable=False),
        sa.Column("retrieval_metrics", sa.JSON(), nullable=False),
        sa.Column("generation_metrics", sa.JSON(), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_evaluation_runs_dataset_id", "evaluation_runs", ["dataset_id"]
    )


def downgrade() -> None:
    op.drop_index("ix_evaluation_runs_dataset_id", table_name="evaluation_runs")
    op.drop_table("evaluation_runs")
