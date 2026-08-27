"""Public session lifecycle response schemas."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class SessionResponse(BaseModel):
    session_id: UUID
    created_at: datetime
    expires_at: datetime