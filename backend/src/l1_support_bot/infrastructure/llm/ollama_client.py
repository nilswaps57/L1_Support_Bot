"""Ollama HTTP adapter; no Ollama SDK leaks into application code."""

from __future__ import annotations

import httpx

from l1_support_bot.application.shared.retry_policy import RetryPolicy, run_with_retry
from l1_support_bot.domain.errors import DomainError, LLMUnavailableError
from l1_support_bot.domain.models.configuration import LLMConfig


class OllamaClient:
    def __init__(self, client: httpx.AsyncClient | None = None) -> None:
        self.client = client
        self._owned_client = client is None

    async def complete(self, prompt: str, *, config: LLMConfig) -> str:
        client = self.client or httpx.AsyncClient(timeout=config.timeout_seconds)
        try:
            request = {
                "model": config.model,
                "prompt": prompt,
                "stream": False,
                "format": "json",
                "options": {
                    "temperature": config.temperature,
                    "num_predict": config.max_tokens,
                    "num_ctx": config.context_window,
                },
            }
            async def request_once() -> str:
                response = await client.post(
                    f"{config.endpoint.rstrip('/')}/api/generate", json=request
                )
                response.raise_for_status()
                value = response.json().get("response")
                if not isinstance(value, str) or not value.strip():
                    raise ValueError("invalid model response")
                return value

            return await run_with_retry(
                request_once,
                policy=RetryPolicy(max_attempts=config.max_retries + 1),
                idempotent=True,
            )
        except LLMUnavailableError:
            raise
        except DomainError as exc:
            raise LLMUnavailableError() from exc
        except (httpx.HTTPError, ValueError, KeyError, TypeError) as exc:
            raise LLMUnavailableError("Answer generation is temporarily unavailable.") from exc
        finally:
            if self._owned_client:
                await client.aclose()

    async def health_check(self, *, config: LLMConfig) -> bool:
        client = self.client or httpx.AsyncClient(timeout=config.timeout_seconds)
        try:
            response = await client.get(f"{config.endpoint.rstrip('/')}/api/tags")
            response.raise_for_status()
            models = response.json().get("models", [])
            return any(
                model.get("name") == config.model
                for model in models
                if isinstance(model, dict)
            )
        except (httpx.HTTPError, ValueError, TypeError):
            return False
        finally:
            if self._owned_client:
                await client.aclose()
