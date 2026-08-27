"""Initial chat-session creation route."""

from uuid import UUID

from fastapi import APIRouter, Request, Response

from l1_support_bot.application.session.session_manager import SessionManager
from l1_support_bot.application.session.start_chat_session import StartChatSession
from l1_support_bot.interface.dependencies import get_dependencies
from l1_support_bot.interface.dto.sessions import SessionResponse

router = APIRouter(prefix="/sessions", tags=["sessions"])


@router.post("", response_model=SessionResponse, status_code=201)
async def start_session(request: Request) -> SessionResponse:
    settings = request.app.state.settings
    store = get_dependencies(request).session_store
    session = await StartChatSession(
        settings.session_ttl_minutes,
        store,
        history_window_turns=settings.session_history_window_turns,
        history_token_budget=settings.session_history_token_budget,
    ).execute()
    return SessionResponse(
        session_id=session.id,
        created_at=session.created_at,
        expires_at=session.expires_at,
    )


@router.delete("/{session_id}", status_code=204)
async def clear_session(request: Request, session_id: UUID) -> Response:
    store = get_dependencies(request).session_store
    if store is None:
        from l1_support_bot.domain.errors import SessionNotFoundError

        raise SessionNotFoundError()
    settings = request.app.state.settings
    await SessionManager(
        store,
        ttl_minutes=settings.session_ttl_minutes,
        history_window_turns=settings.session_history_window_turns,
        history_token_budget=settings.session_history_token_budget,
    ).clear(session_id)
    return Response(status_code=204)
