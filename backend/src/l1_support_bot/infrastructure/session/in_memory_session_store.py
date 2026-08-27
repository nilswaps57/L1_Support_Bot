"""Non-persistent session storage for the initial release."""

from collections.abc import Sequence
from uuid import UUID

from l1_support_bot.domain.models.answer import Answer
from l1_support_bot.domain.models.session import ChatMessage, ChatSession


class InMemorySessionStore:
    def __init__(self, *, max_messages: int = 20) -> None:
        if max_messages < 2:
            raise ValueError("Session storage must retain at least one turn")
        self.max_messages = max_messages
        self.sessions: dict[UUID, ChatSession] = {}
        self.messages: dict[UUID, list[ChatMessage]] = {}
        self.answer_contexts: dict[tuple[UUID, UUID], Answer] = {}

    async def get(self, session_id: UUID) -> ChatSession | None:
        return self.sessions.get(session_id)

    async def save(self, session: ChatSession) -> None:
        self.sessions[session.id] = session
        self.messages.setdefault(session.id, [])

    async def delete(self, session_id: UUID) -> None:
        self.sessions.pop(session_id, None)
        self.messages.pop(session_id, None)
        for key in tuple(self.answer_contexts):
            if key[0] == session_id:
                del self.answer_contexts[key]

    async def get_messages(self, session_id: UUID, *, limit: int) -> Sequence[ChatMessage]:
        if limit < 1:
            return ()
        return tuple(self.messages.get(session_id, ())[-limit:])

    async def append_message(self, message: ChatMessage) -> None:
        if message.session_id not in self.sessions:
            return
        messages = self.messages.setdefault(message.session_id, [])
        messages.append(message)
        del messages[:-self.max_messages]

    async def save_answer_context(self, session_id: UUID, answer: Answer) -> None:
        self.answer_contexts[(session_id, answer.answer_id)] = answer

    async def get_answer_context(self, session_id: UUID, answer_id: UUID) -> Answer | None:
        return self.answer_contexts.get((session_id, answer_id))