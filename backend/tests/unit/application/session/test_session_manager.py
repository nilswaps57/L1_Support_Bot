from datetime import UTC, datetime, timedelta
from uuid import uuid4

import pytest

from l1_support_bot.application.session.session_manager import SessionManager
from l1_support_bot.domain.errors import SessionNotFoundError
from l1_support_bot.domain.models.session import ChatMessage, MessageRole
from l1_support_bot.infrastructure.session.in_memory_session_store import InMemorySessionStore


@pytest.mark.asyncio
async def test_create_persists_session_and_records_bounded_messages() -> None:
    store = InMemorySessionStore()
    manager = SessionManager(
        store,
        ttl_minutes=30,
        history_window_turns=2,
        history_token_budget=100,
    )

    session = await manager.create()
    await manager.record_turn(session.id, "What is BA435?", "BA435 opens the account screen.")

    active = await manager.require_active(session.id)
    history = await manager.history(session.id)

    assert active.last_active_at >= session.last_active_at
    assert [message.role for message in history] == [MessageRole.USER, MessageRole.ASSISTANT]
    assert [message.content for message in history] == [
        "What is BA435?",
        "BA435 opens the account screen.",
    ]


@pytest.mark.asyncio
async def test_expired_session_is_removed_and_cannot_be_reused() -> None:
    store = InMemorySessionStore()
    current_time = [datetime(2026, 8, 27, 10, 0, tzinfo=UTC)]
    manager = SessionManager(
        store,
        ttl_minutes=5,
        clock=lambda: current_time[0],
    )
    session = await manager.create()
    await store.append_message(
        ChatMessage(session.id, MessageRole.USER, "What is BA435?", turn_order=0)
    )
    current_time[0] += timedelta(minutes=6)

    with pytest.raises(SessionNotFoundError):
        await manager.history(session.id)

    assert await store.get(session.id) is None


@pytest.mark.asyncio
async def test_clear_wipes_history_and_requires_a_new_session() -> None:
    store = InMemorySessionStore()
    manager = SessionManager(store, ttl_minutes=30)
    session = await manager.create()
    await manager.record_turn(session.id, "What is BA435?", "It opens the account screen.")

    await manager.clear(session.id)

    assert await store.get(session.id) is None
    with pytest.raises(SessionNotFoundError):
        await manager.history(session.id)


@pytest.mark.asyncio
async def test_missing_session_is_safe_and_does_not_create_implicit_context() -> None:
    manager = SessionManager(InMemorySessionStore(), ttl_minutes=30)

    with pytest.raises(SessionNotFoundError):
        await manager.require_active(uuid4())


@pytest.mark.asyncio
async def test_record_turn_keeps_the_configured_history_window() -> None:
    store = InMemorySessionStore()
    manager = SessionManager(
        store,
        ttl_minutes=30,
        history_window_turns=1,
        history_token_budget=1_000,
    )
    session = await manager.create()
    await manager.record_turn(session.id, "first question", "first answer")
    await manager.record_turn(session.id, "second question", "second answer")

    history = await manager.history(session.id)

    assert [message.content for message in history] == ["second question", "second answer"]