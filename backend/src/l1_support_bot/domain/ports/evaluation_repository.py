"""Persistence port for reproducible evaluation records."""

from typing import Protocol

from l1_support_bot.domain.models.evaluation import EvaluationRun


class EvaluationRepository(Protocol):
    async def save(self, run: EvaluationRun) -> EvaluationRun: ...
