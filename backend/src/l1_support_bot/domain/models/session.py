"""Bounded chat-session domain values."""

from dataclasses import dataclass, field, replace
from datetime import UTC, datetime, timedelta
from enum import StrEnum
from uuid import UUID, uuid4


class MessageRole(StrEnum):
    USER = "user"
    ASSISTANT = "assistant"


@dataclass(frozen=True, slots=True)
class ChatSession:
    id: UUID
    created_at: datetime
    last_active_at: datetime
    expires_at: datetime
    is_active: bool = True

    def __post_init__(self) -> None:
        if self.expires_at <= self.created_at:
            raise ValueError("Session must expire after creation")

    @classmethod
    def new(cls, *, ttl: timedelta, now: datetime | None = None) -> "ChatSession":
        if ttl <= timedelta(0):
            raise ValueError("Session TTL must be positive")
        current = now or datetime.now(UTC)
        return cls(uuid4(), current, current, current + ttl)

    def is_expired(self, now: datetime | None = None) -> bool:
        return not self.is_active or (now or datetime.now(UTC)) >= self.expires_at

    def touch(self, *, ttl: timedelta, now: datetime | None = None) -> "ChatSession":
        if self.is_expired(now):
            return replace(self, is_active=False)
        current = now or datetime.now(UTC)
        return replace(self, last_active_at=current, expires_at=current + ttl)


@dataclass(frozen=True, slots=True)
class ChatMessage:
    session_id: UUID
    role: MessageRole
    content: str
    turn_order: int
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def __post_init__(self) -> None:
        if not self.content.strip():
            raise ValueError("Chat message cannot be empty")
        if self.turn_order < 0:
            raise ValueError("Chat message order must be non-negative")