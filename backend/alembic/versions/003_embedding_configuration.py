"""Persist embedding configuration and compatibility identity."""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "003_embedding_configuration"
down_revision: str | None = "002_chunks_and_ingestion_diagnostics"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    connection = op.get_bind()
    inspector = sa.inspect(connection)
    chunk_columns = {item["name"] for item in inspector.get_columns("knowledge_chunks")}
    job_columns = {item["name"] for item in inspector.get_columns("ingestion_jobs")}
    if "source_type" not in chunk_columns:
        op.add_column(
            "knowledge_chunks",
            sa.Column("source_type", sa.String(length=50), nullable=True),
        )
    if "embedding_config_id" not in job_columns:
        op.add_column(
            "ingestion_jobs",
            sa.Column("embedding_config_id", sa.String(length=36), nullable=True),
        )
    if "embedding_configurations" not in set(inspector.get_table_names()):
        op.create_table(
            "embedding_configurations",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("provider", sa.String(length=50), nullable=False),
        sa.Column("model", sa.String(length=200), nullable=False),
        sa.Column("model_version", sa.String(length=100), nullable=False),
        sa.Column("endpoint", sa.String(length=500), nullable=False),
        sa.Column("dimensions", sa.Integer(), nullable=False),
        sa.Column("distance_method", sa.String(length=20), nullable=False),
        sa.Column("index_compat_id", sa.String(length=300), nullable=False),
        sa.Column("batch_size", sa.Integer(), nullable=False),
        sa.Column("timeout_seconds", sa.Integer(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("label", sa.String(length=200), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        )
        op.create_index(
            "ix_embedding_configurations_active",
            "embedding_configurations",
            ["is_active", "updated_at"],
        )


def downgrade() -> None:
    connection = op.get_bind()
    inspector = sa.inspect(connection)
    tables = set(inspector.get_table_names())
    if "embedding_configurations" in tables:
        indexes = {item["name"] for item in inspector.get_indexes("embedding_configurations")}
        if "ix_embedding_configurations_active" in indexes:
            op.drop_index(
                "ix_embedding_configurations_active",
                table_name="embedding_configurations",
            )
        op.drop_table("embedding_configurations")
    job_columns = {item["name"] for item in inspector.get_columns("ingestion_jobs")}
    chunk_columns = {item["name"] for item in inspector.get_columns("knowledge_chunks")}
    if "embedding_config_id" in job_columns:
        op.drop_column("ingestion_jobs", "embedding_config_id")
    if "source_type" in chunk_columns:
        op.drop_column("knowledge_chunks", "source_type")
