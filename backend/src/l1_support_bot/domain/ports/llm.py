"""Language-model inference contract."""

from typing import Protocol

from l1_support_bot.domain.models.configuration import LLMConfig


class LLMPort(Protocol):
    async def complete(self, prompt: str, *, config: LLMConfig) -> str: ...

    async def health_check(self, *, config: LLMConfig) -> bool: ...
