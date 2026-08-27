import httpx
import pytest

from l1_support_bot.domain.models.configuration import EmbeddingConfig
from l1_support_bot.infrastructure.embedding.http_embedding import HttpEmbeddingAdapter


def config() -> EmbeddingConfig:
    return EmbeddingConfig(
        provider="openai_compatible",
        model="deterministic",
        model_version="1",
        endpoint="https://embedding.test/v1",
        dimensions=3,
        index_compat_id="openai_compatible:deterministic:1:3",
    )


@pytest.mark.asyncio
async def test_http_embedding_supports_batch_query_and_dimensions() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"data": [{"embedding": [1.0, 2.0, 3.0]}]})

    adapter = HttpEmbeddingAdapter(client=httpx.AsyncClient(transport=httpx.MockTransport(handler)))

    vectors = await adapter.embed_batch(["BA435"], config())
    query = await adapter.embed_query("What is BA435?", config())

    assert vectors == ((1.0, 2.0, 3.0),)
    assert query == (1.0, 2.0, 3.0)
    assert await adapter.get_dimensions(config()) == 3


@pytest.mark.asyncio
async def test_http_embedding_maps_provider_failure_safely() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(503, text="provider unavailable")

    adapter = HttpEmbeddingAdapter(client=httpx.AsyncClient(transport=httpx.MockTransport(handler)))

    with pytest.raises(Exception, match="Embedding service is temporarily unavailable"):
        await adapter.embed_query("BA435", config())
