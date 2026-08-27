"""Bounded embedding connectivity and dimension validation."""

from l1_support_bot.application.configuration.validate_llm import ConnectivityValidation
from l1_support_bot.domain.errors import EmbeddingConnectivityError
from l1_support_bot.domain.models.configuration import EmbeddingConfig
from l1_support_bot.domain.ports.embedding import EmbeddingPort


class ValidateEmbedding:
    def __init__(self, client: EmbeddingPort) -> None:
        self.client = client

    async def execute(self, config: EmbeddingConfig) -> ConnectivityValidation:
        try:
            vector = await self.client.embed_query("health check", config)
        except Exception as exc:
            raise EmbeddingConnectivityError(
                "The configured embedding endpoint could not be validated."
            ) from exc
        if len(vector) != config.dimensions:
            raise EmbeddingConnectivityError(
                "The configured embedding endpoint returned incompatible dimensions."
            )
        return ConnectivityValidation(
            category="embedding", status="ok", model=config.model, latency_ms=0
        )
