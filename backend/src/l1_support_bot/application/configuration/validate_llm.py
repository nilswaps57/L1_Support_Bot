"""Bounded LLM connectivity validation."""

from dataclasses import asdict, dataclass

from l1_support_bot.domain.errors import LLMConnectivityError
from l1_support_bot.domain.models.configuration import LLMConfig
from l1_support_bot.domain.ports.llm import LLMPort


@dataclass(frozen=True, slots=True)
class ConnectivityValidation:
    category: str
    status: str
    model: str
    latency_ms: int

    def as_dict(self) -> dict[str, object]:
        return asdict(self)


class ValidateLLM:
    def __init__(self, client: LLMPort) -> None:
        self.client = client

    async def execute(self, config: LLMConfig) -> ConnectivityValidation:
        try:
            healthy = await self.client.health_check(config=config)
        except Exception as exc:
            raise LLMConnectivityError(
                "The configured LLM endpoint could not be validated."
            ) from exc
        if not healthy:
            raise LLMConnectivityError("The configured LLM endpoint could not be validated.")
        return ConnectivityValidation(category="llm", status="ok", model=config.model, latency_ms=0)
