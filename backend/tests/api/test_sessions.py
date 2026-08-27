from datetime import UTC, datetime, timedelta

from fastapi.testclient import TestClient

from l1_support_bot.domain.models.session import ChatMessage, ChatSession, MessageRole
from l1_support_bot.infrastructure.session.in_memory_session_store import InMemorySessionStore
from l1_support_bot.interface.api.main import create_app
from l1_support_bot.interface.config import Settings
from l1_support_bot.interface.dependencies import PortDependencies


def test_create_and_clear_session_wipes_context() -> None:
    store = InMemorySessionStore()
    client = TestClient(
        create_app(
            Settings(session_ttl_minutes=30),
            dependencies=PortDependencies(session_store=store),
        )
    )

    created = client.post("/api/v1/sessions")
    session_id = created.json()["session_id"]

    response = client.delete(f"/api/v1/sessions/{session_id}")

    assert created.status_code == 201
    assert response.status_code == 204
    assert session_id not in {str(identifier) for identifier in store.sessions}
    assert not store.messages


def test_chat_with_expired_session_returns_safe_not_found_response() -> None:
    store = InMemorySessionStore()
    session = ChatSession.new(
        ttl=timedelta(minutes=1),
        now=datetime.now(UTC) - timedelta(minutes=2),
    )
    store.sessions[session.id] = session
    client = TestClient(
        create_app(
            Settings(session_ttl_minutes=30),
            dependencies=PortDependencies(
                session_store=store,
                retriever=object(),
                llm=object(),
            ),
        )
    )

    response = client.post(
        "/api/v1/chat",
        json={"session_id": str(session.id), "question": "What is it?"},
    )

    assert response.status_code == 404
    assert response.json()["error_code"] == "SESSION_NOT_FOUND"


def test_expired_session_returns_not_found_without_exposing_history() -> None:
    store = InMemorySessionStore()
    session = ChatSession.new(
        ttl=timedelta(minutes=1),
        now=datetime.now(UTC) - timedelta(minutes=2),
    )
    store.sessions[session.id] = session
    store.messages[session.id] = [
        ChatMessage(session.id, MessageRole.USER, "What is BA435?", 0)
    ]
    client = TestClient(
        create_app(
            Settings(session_ttl_minutes=30),
            dependencies=PortDependencies(session_store=store),
        )
    )

    response = client.delete(f"/api/v1/sessions/{session.id}")

    assert response.status_code == 404
    assert response.json()["error_code"] == "SESSION_NOT_FOUND"
    assert session.id not in store.messages
