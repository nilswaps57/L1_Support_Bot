"""Bounded chat-session storage contract."""

from collections.abc import Sequence
from typing import Protocol
from uuid import UUID

from l1_support_bot.domain.models.answer import Answer
from l1_support_bot.domain.models.session import ChatMessage, ChatSession


class SessionStore(Protocol):
    async def get(self, session_id: UUID) -> ChatSession | None: ...

    async def save(self, session: ChatSession) -> None: ...

    async def delete(self, session_id: UUID) -> None: ...

    async def get_messages(self, session_id: UUID, *, limit: int) -> Sequence[ChatMessage]: ...

    async def append_message(self, message: ChatMessage) -> None: ...

    async def save_answer_context(self, session_id: UUID, answer: Answer) -> None: ...

    async def get_answer_context(self, session_id: UUID, answer_id: UUID) -> Answer | None: ...
