"""Persist supervised answer feedback snapshots."""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "006_feedback"
down_revision: str | None = "005_document_lifecycle_generations"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "feedback",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("answer_id", sa.String(length=36), nullable=False),
        sa.Column("session_id", sa.String(length=36), nullable=True),
        sa.Column("question", sa.Text(), nullable=False),
        sa.Column("answer_text", sa.Text(), nullable=False),
        sa.Column("answer_type", sa.String(length=20), nullable=False),
        sa.Column("rating", sa.String(length=20), nullable=False),
        sa.Column("comment", sa.String(length=1000), nullable=True),
        sa.Column("llm_config_id", sa.String(length=36), nullable=True),
        sa.Column("embedding_config_id", sa.String(length=36), nullable=True),
        sa.Column("retrieval_config_id", sa.String(length=36), nullable=True),
        sa.Column("retrieved_chunk_ids", sa.JSON(), nullable=False),
        sa.Column("insufficient_information", sa.Boolean(), nullable=False),
        sa.Column("submitted_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("answer_id", name="uq_feedback_answer_id"),
    )
    op.create_index("ix_feedback_session_id", "feedback", ["session_id"])


def downgrade() -> None:
    op.drop_index("ix_feedback_session_id", table_name="feedback")
    op.drop_table("feedback")