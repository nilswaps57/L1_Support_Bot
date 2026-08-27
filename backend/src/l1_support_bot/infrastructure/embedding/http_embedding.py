"""OpenAI-compatible HTTP embedding adapter."""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any

import httpx

from l1_support_bot.domain.errors import DomainError, ErrorCategory
from l1_support_bot.domain.models.configuration import EmbeddingConfig


class EmbeddingUnavailableError(DomainError):
    category = ErrorCategory.UNAVAILABLE_SERVICE
    code = "EMBEDDING_UNAVAILABLE"


class HttpEmbeddingAdapter:
    def __init__(self, client: httpx.AsyncClient | None = None) -> None:
        self.client = client
        self._owned_client = client is None

    async def embed_batch(
        self, texts: Sequence[str], config: EmbeddingConfig
    ) -> Sequence[Sequence[float]]:
        if not texts:
            return ()
        client = self.client or httpx.AsyncClient(timeout=config.timeout_seconds)
        try:
            response = await client.post(
                self._endpoint(config),
                headers=self._headers(),
                json={"model": config.model, "input": list(texts)},
            )
            response.raise_for_status()
            vectors = self._vectors(response.json())
            if len(vectors) != len(texts):
                raise EmbeddingUnavailableError("Embedding service returned an invalid batch.")
            self._validate_dimensions(vectors, config)
            return vectors
        except EmbeddingUnavailableError:
            raise
        except (httpx.HTTPError, ValueError, KeyError, TypeError) as exc:
            raise EmbeddingUnavailableError(
                "Embedding service is temporarily unavailable."
            ) from exc
        finally:
            if self._owned_client:
                await client.aclose()

    async def embed_query(self, text: str, config: EmbeddingConfig) -> Sequence[float]:
        vectors = await self.embed_batch((text,), config)
        return vectors[0]

    async def get_dimensions(self, config: EmbeddingConfig) -> int:
        return config.dimensions

    async def health_check(self, config: EmbeddingConfig) -> bool:
        try:
            await self.embed_query("health check", config)
            return True
        except EmbeddingUnavailableError:
            return False

    @staticmethod
    def _endpoint(config: EmbeddingConfig) -> str:
        return f"{config.endpoint.rstrip('/')}/embeddings"

    @staticmethod
    def _headers() -> dict[str, str]:
        return {"Content-Type": "application/json"}

    @staticmethod
    def _vectors(payload: Any) -> tuple[tuple[float, ...], ...]:
        rows = payload["data"]
        ordered = sorted(rows, key=lambda row: row.get("index", 0))
        return tuple(tuple(float(value) for value in row["embedding"]) for row in ordered)

    @staticmethod
    def _validate_dimensions(
        vectors: Sequence[Sequence[float]], config: EmbeddingConfig
    ) -> None:
        if any(len(vector) != config.dimensions for vector in vectors):
            raise EmbeddingUnavailableError(
                "Embedding service returned vectors with incompatible dimensions."
            )
