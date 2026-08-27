"""Canonical Phase 14 name for the active configuration repository."""

from l1_support_bot.infrastructure.persistence.sqlalchemy.retrieval_config_repository import (
    SqlAlchemyRetrievalConfigRepository,
)


class SqlAlchemyConfigurationRepository(SqlAlchemyRetrievalConfigRepository):
    """Expose the complete configuration repository under its domain name."""
