"""Health response contract."""

from typing import Literal

from pydantic import BaseModel, Field

ComponentStatus = Literal["available", "unavailable"]


class HealthResponse(BaseModel):
    status: Literal["healthy", "degraded"]
    version: str
    database: ComponentStatus
    vector_store: ComponentStatus
    llm: ComponentStatus
    embedding: ComponentStatus
    degraded_capabilities: list[str] = Field(default_factory=list)
    capabilities: dict[str, bool] = Field(default_factory=dict)