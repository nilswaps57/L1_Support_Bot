"""Domain value object for reproducible RAG evaluation runs."""

from collections.abc import Mapping
from dataclasses import dataclass, field
from datetime import UTC, datetime
from types import MappingProxyType
from uuid import UUID, uuid4


@dataclass(frozen=True, slots=True)
class EvaluationRun:
    dataset_id: str
    configuration_snapshot: Mapping[str, object]
    retrieval_metrics: Mapping[str, object]
    generation_metrics: Mapping[str, object]
    id: UUID = field(default_factory=uuid4)
    started_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def __post_init__(self) -> None:
        if not self.dataset_id.strip():
            raise ValueError("Evaluation dataset identity is required")
        if self.started_at.tzinfo is None:
            raise ValueError("Evaluation timestamp must include timezone information")
        object.__setattr__(
            self, "configuration_snapshot", MappingProxyType(dict(self.configuration_snapshot))
        )
        object.__setattr__(
            self, "retrieval_metrics", MappingProxyType(dict(self.retrieval_metrics))
        )
        object.__setattr__(
            self, "generation_metrics", MappingProxyType(dict(self.generation_metrics))
        )
