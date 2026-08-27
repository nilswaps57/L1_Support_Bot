"""Session lifecycle and bounded history orchestration."""

from collections.abc import Callable
from datetime import UTC, datetime, timedelta
from uuid import UUID

from l1_support_bot.application.session.query_resolution import QueryResolution
from l1_support_bot.domain.errors import SessionNotFoundError
from l1_support_bot.domain.models.answer import Answer
from l1_support_bot.domain.models.session import ChatMessage, ChatSession, MessageRole
from l1_support_bot.domain.ports.session_store import SessionStore


class SessionManager:
    def __init__(
        self,
        store: SessionStore,
        *,
        ttl_minutes: int,
        history_window_turns: int = 10,
        history_token_budget: int = 2_000,
        clock: Callable[[], datetime] | None = None,
    ) -> None:
        if ttl_minutes < 1:
            raise ValueError("Session TTL must be positive")
        if history_window_turns < 1 or history_token_budget < 1:
            raise ValueError("Session history limits must be positive")
        self.store = store
        self.ttl = timedelta(minutes=ttl_minutes)
        self.history_window_turns = history_window_turns
        self.history_token_budget = history_token_budget
        self.clock = clock or (lambda: datetime.now(UTC))

    async def create(self, *, now: datetime | None = None) -> ChatSession:
        session = ChatSession.new(ttl=self.ttl, now=now or self.clock())
        await self.store.save(session)
        return session

    async def require_active(self, session_id: UUID) -> ChatSession:
        session = await self.store.get(session_id)
        if session is None:
            raise SessionNotFoundError()
        current = self.clock()
        if session.is_expired(current):
            await self.store.delete(session_id)
            raise SessionNotFoundError()
        return session

    async def history(self, session_id: UUID) -> tuple[ChatMessage, ...]:
        await self.require_active(session_id)
        messages = await self.store.get_messages(
            session_id,
            limit=self.history_window_turns * 2,
        )
        return QueryResolution(
            history_window_turns=self.history_window_turns,
            token_budget=self.history_token_budget,
        ).select_history(messages)

    async def record_turn(
        self, session_id: UUID, question: str, answer: str, answer_context: Answer | None = None
    ) -> None:
        session = await self.require_active(session_id)
        existing = await self.store.get_messages(session_id, limit=self.history_window_turns * 2)
        turn_order = existing[-1].turn_order + 1 if existing else 0
        await self.store.append_message(
            ChatMessage(session_id, MessageRole.USER, question, turn_order)
        )
        await self.store.append_message(
            ChatMessage(session_id, MessageRole.ASSISTANT, answer, turn_order + 1)
        )
        if answer_context is not None:
            await self.store.save_answer_context(session_id, answer_context)
        await self.store.save(session.touch(ttl=self.ttl, now=self.clock()))

    async def clear(self, session_id: UUID) -> None:
        await self.require_active(session_id)
        await self.store.delete(session_id)