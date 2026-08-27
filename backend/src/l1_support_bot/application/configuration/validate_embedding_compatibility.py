"""Prevent silent use of vectors built with another embedding model."""

from l1_support_bot.domain.errors import IncompatibleIndexError
from l1_support_bot.domain.models.configuration import EmbeddingConfig


class ValidateEmbeddingCompatibility:
    async def execute(
        self,
        *,
        active: EmbeddingConfig,
        indexed_model_id: str | None,
        confirm_reindex: bool = False,
    ) -> bool:
        if indexed_model_id is None or indexed_model_id == active.embedding_model_id:
            return True
        if not confirm_reindex:
            raise IncompatibleIndexError(
                "Changing the embedding model requires confirmed re-indexing."
            )
        return True
