import httpx
import pytest

from l1_support_bot.domain.models.configuration import LLMConfig
from l1_support_bot.infrastructure.llm.ollama_client import OllamaClient


def config() -> LLMConfig:
    return LLMConfig(provider="ollama", model="test", endpoint="http://ollama.test")


@pytest.mark.asyncio
async def test_ollama_client_returns_structured_response() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"response": '{"answer_text":"BA435"}'})

    client = OllamaClient(client=httpx.AsyncClient(transport=httpx.MockTransport(handler)))
    assert await client.complete("prompt", config=config()) == '{"answer_text":"BA435"}'


@pytest.mark.asyncio
async def test_ollama_health_check_is_safe_on_failure() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(503)

    client = OllamaClient(client=httpx.AsyncClient(transport=httpx.MockTransport(handler)))
    assert not await client.health_check(config=config())
