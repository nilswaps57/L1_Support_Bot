"""Create a session token without implementing Phase 6 history behavior."""

from datetime import timedelta

from l1_support_bot.domain.models.session import ChatSession


class StartChatSession:
    def __init__(self, ttl_minutes: int) -> None:
        self.ttl = timedelta(minutes=ttl_minutes)

    async def execute(self) -> ChatSession:
        return ChatSession.new(ttl=self.ttl)
