"""Create and persist a bounded chat session."""

from l1_support_bot.application.session.session_manager import SessionManager
from l1_support_bot.domain.models.session import ChatSession
from l1_support_bot.domain.ports.session_store import SessionStore


class StartChatSession:
    def __init__(
        self,
        ttl_minutes: int,
        session_store: SessionStore | None = None,
        *,
        history_window_turns: int = 10,
        history_token_budget: int = 2_000,
    ) -> None:
        self.session_store = session_store
        self.manager = (
            SessionManager(
                session_store,
                ttl_minutes=ttl_minutes,
                history_window_turns=history_window_turns,
                history_token_budget=history_token_budget,
            )
            if session_store is not None
            else None
        )
        self.ttl_minutes = ttl_minutes

    async def execute(self) -> ChatSession:
        if self.manager is None:
            from datetime import timedelta

            return ChatSession.new(ttl=timedelta(minutes=self.ttl_minutes))
        return await self.manager.create()
