"""Persist document lifecycle compatibility metadata."""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "005_document_lifecycle_generations"
down_revision: str | None = "004_retrieval_configuration"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "ingestion_jobs",
        sa.Column("chunking_config_snapshot", sa.String(length=1000), nullable=True),
    )
    op.add_column(
        "knowledge_chunks",
        sa.Column("index_generation_id", sa.String(length=300), nullable=True),
    )
    op.create_index(
        "ix_knowledge_chunks_index_generation_id",
        "knowledge_chunks",
        ["index_generation_id"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_knowledge_chunks_index_generation_id", table_name="knowledge_chunks"
    )
    op.drop_column("knowledge_chunks", "index_generation_id")
    op.drop_column("ingestion_jobs", "chunking_config_snapshot")
