"""Runtime dependency and degraded-capability state."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

ComponentStatus = Literal["available", "unavailable"]


@dataclass(slots=True)
class RuntimeHealthState:
    database: ComponentStatus = "available"
    vector_store: ComponentStatus = "available"
    llm: ComponentStatus = "available"
    embedding: ComponentStatus = "available"
    _degraded_capabilities: set[str] = field(default_factory=set)

    @property
    def persistence_available(self) -> bool:
        return self.database == "available"

    @property
    def degraded(self) -> bool:
        return (
            bool(self._degraded_capabilities)
            or not self.persistence_available
            or any(
                status == "unavailable"
                for status in (self.vector_store, self.llm, self.embedding)
            )
        )

    @property
    def degraded_capabilities(self) -> list[str]:
        return sorted(self._degraded_capabilities)

    def mark_database(self, available: bool) -> None:
        self.database = "available" if available else "unavailable"
        if available:
            self._degraded_capabilities.clear()
        else:
            self._degraded_capabilities.update(
                {"document_management", "configuration_mutations", "feedback_submission"}
            )

    def mark_component(self, component: str, available: bool) -> None:
        if component in {"database", "vector_store", "llm", "embedding"}:
            setattr(self, component, "available" if available else "unavailable")
            capability = (
                "chat_unavailable"
                if component in {"vector_store", "llm"}
                else f"{component}_unavailable"
            )
            if available:
                self._degraded_capabilities.discard(capability)
            else:
                self._degraded_capabilities.add(capability)

    def mark_read_only_chat(self) -> None:
        self._degraded_capabilities.add("chat_read_only")

    def mark_normal(self) -> None:
        self._degraded_capabilities.clear()
        self.database = "available"


def health_snapshot(state: RuntimeHealthState) -> dict[str, object]:
    return {
        "status": "degraded" if state.degraded else "healthy",
        "database": state.database,
        "vector_store": state.vector_store,
        "llm": state.llm,
        "embedding": state.embedding,
        "degraded_capabilities": state.degraded_capabilities,
        "capabilities": {
            "chat": state.llm == "available" and state.vector_store == "available",
            "document_management": state.persistence_available,
            "configuration_mutations": state.persistence_available,
            "feedback_submission": state.persistence_available,
        },
    }