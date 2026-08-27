"""Persistence contract for supervised answer feedback."""

from collections.abc import Sequence
from typing import Protocol
from uuid import UUID

from l1_support_bot.domain.models.feedback import Feedback


class FeedbackRepository(Protocol):
    async def save(self, feedback: Feedback) -> Feedback: ...

    async def get_by_answer(self, answer_id: UUID) -> Feedback | None: ...

    async def list_by_answer(self, answer_id: UUID) -> Sequence[Feedback]: ...

    async def list_by_session(self, session_id: UUID) -> Sequence[Feedback]: ...