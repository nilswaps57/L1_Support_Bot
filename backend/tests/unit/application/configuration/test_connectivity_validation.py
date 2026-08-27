import pytest

from l1_support_bot.application.configuration.validate_embedding import ValidateEmbedding
from l1_support_bot.application.configuration.validate_llm import ValidateLLM
from l1_support_bot.domain.errors import EmbeddingConnectivityError, LLMConnectivityError
from l1_support_bot.domain.models.configuration import EmbeddingConfig, LLMConfig


class LLMProbe:
    def __init__(self, result: bool | Exception) -> None:
        self.result = result

    async def health_check(self, *, config: LLMConfig) -> bool:
        if isinstance(self.result, Exception):
            raise self.result
        return self.result


class EmbeddingProbe:
    def __init__(self, result: tuple[float, ...] | Exception) -> None:
        self.result = result

    async def embed_query(self, text: str, config: EmbeddingConfig) -> tuple[float, ...]:
        if isinstance(self.result, Exception):
            raise self.result
        return self.result


def llm() -> LLMConfig:
    return LLMConfig(provider="fake", model="test", endpoint="https://llm.test", timeout_seconds=2)


def embedding() -> EmbeddingConfig:
    return EmbeddingConfig(
        provider="fake", model="test", model_version="1", endpoint="https://embed.test",
        dimensions=3, index_compat_id="fake:test:1:3", timeout_seconds=2,
    )


@pytest.mark.asyncio
async def test_llm_connectivity_success_and_unavailable_are_distinguished() -> None:
    result = await ValidateLLM(LLMProbe(True)).execute(llm())
    assert result.status == "ok"

    with pytest.raises(LLMConnectivityError):
        await ValidateLLM(LLMProbe(False)).execute(llm())
    with pytest.raises(LLMConnectivityError):
        await ValidateLLM(LLMProbe(TimeoutError())).execute(llm())


@pytest.mark.asyncio
async def test_embedding_connectivity_checks_dimensions_and_provider_failures() -> None:
    result = await ValidateEmbedding(EmbeddingProbe((0.1, 0.2, 0.3))).execute(embedding())
    assert result.status == "ok"

    for failure in ((0.1,), PermissionError("authentication failed"), ConnectionError("down")):
        with pytest.raises(EmbeddingConnectivityError):
            await ValidateEmbedding(EmbeddingProbe(failure)).execute(embedding())
