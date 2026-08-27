"""Initial chat-session creation route."""

from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Request
from pydantic import BaseModel

from l1_support_bot.application.session.start_chat_session import StartChatSession

router = APIRouter(prefix="/sessions", tags=["sessions"])


class SessionResponse(BaseModel):
    session_id: UUID
    created_at: datetime
    expires_at: datetime


@router.post("", response_model=SessionResponse, status_code=201)
async def start_session(request: Request) -> SessionResponse:
    session = await StartChatSession(request.app.state.settings.session_ttl_minutes).execute()
    return SessionResponse(
        session_id=session.id,
        created_at=session.created_at,
        expires_at=session.expires_at,
    )
