import pytest

from l1_support_bot.application.configuration.validate_embedding_compatibility import (
    ValidateEmbeddingCompatibility,
)
from l1_support_bot.domain.errors import IncompatibleIndexError
from l1_support_bot.domain.models.configuration import EmbeddingConfig


def config(model: str) -> EmbeddingConfig:
    return EmbeddingConfig(
        provider="test", model=model, model_version="1", endpoint="https://embed.test",
        dimensions=3, index_compat_id=f"test:{model}:1:3",
    )


@pytest.mark.asyncio
async def test_same_model_or_empty_index_is_compatible() -> None:
    policy = ValidateEmbeddingCompatibility()
    assert await policy.execute(active=config("one"), indexed_model_id=None)
    assert await policy.execute(active=config("one"), indexed_model_id="test:one:1:3")


@pytest.mark.asyncio
async def test_model_change_requires_explicit_reindex_confirmation() -> None:
    policy = ValidateEmbeddingCompatibility()

    with pytest.raises(IncompatibleIndexError):
        await policy.execute(active=config("two"), indexed_model_id="test:one:1:3")

    assert await policy.execute(
        active=config("two"), indexed_model_id="test:one:1:3", confirm_reindex=True
    )
