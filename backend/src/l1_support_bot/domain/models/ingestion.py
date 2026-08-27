"""Document ingestion lifecycle and job state."""

from dataclasses import dataclass, field, replace
from datetime import UTC, datetime
from enum import StrEnum
from typing import Final
from uuid import UUID, uuid4

from l1_support_bot.domain.models.parsed_document import ParseWarning


class IngestionStatus(StrEnum):
    UPLOADED = "UPLOADED"
    QUEUED = "QUEUED"
    PARSING = "PARSING"
    NORMALISING = "NORMALISING"
    CHUNKING = "CHUNKING"
    READY_FOR_INDEXING = "READY_FOR_INDEXING"
    READY_FOR_INDEXING_WITH_WARNING = "READY_FOR_INDEXING_WITH_WARNING"
    EMBEDDING = "EMBEDDING"
    INDEXING = "INDEXING"
    COMPLETED = "COMPLETED"
    COMPLETED_WITH_WARNING = "COMPLETED_WITH_WARNING"
    FAILED = "FAILED"
    DELETING = "DELETING"
    DELETED = "DELETED"

    @property
    def is_terminal(self) -> bool:
        return self in {
            IngestionStatus.COMPLETED,
            IngestionStatus.COMPLETED_WITH_WARNING,
            IngestionStatus.FAILED,
            IngestionStatus.DELETED,
        }

    @property
    def is_queryable(self) -> bool:
        return self in {
            IngestionStatus.COMPLETED,
            IngestionStatus.COMPLETED_WITH_WARNING,
        }

    @property
    def is_processing(self) -> bool:
        return self in {
            IngestionStatus.QUEUED,
            IngestionStatus.PARSING,
            IngestionStatus.NORMALISING,
            IngestionStatus.CHUNKING,
            IngestionStatus.READY_FOR_INDEXING,
            IngestionStatus.READY_FOR_INDEXING_WITH_WARNING,
            IngestionStatus.EMBEDDING,
            IngestionStatus.INDEXING,
        }

    def can_transition_to(self, target: "IngestionStatus") -> bool:
        return target in _ALLOWED_TRANSITIONS[self]

    def transition_to(self, target: "IngestionStatus") -> "IngestionStatus":
        if not self.can_transition_to(target):
            raise ValueError(f"Invalid ingestion transition: {self} -> {target}")
        return target


_ALLOWED_TRANSITIONS: Final[dict[IngestionStatus, frozenset[IngestionStatus]]] = {
    IngestionStatus.UPLOADED: frozenset({IngestionStatus.QUEUED, IngestionStatus.DELETING}),
    IngestionStatus.QUEUED: frozenset({IngestionStatus.PARSING, IngestionStatus.FAILED}),
    IngestionStatus.PARSING: frozenset(
        {IngestionStatus.NORMALISING, IngestionStatus.QUEUED, IngestionStatus.FAILED}
    ),
    IngestionStatus.NORMALISING: frozenset(
        {IngestionStatus.CHUNKING, IngestionStatus.QUEUED, IngestionStatus.FAILED}
    ),
    IngestionStatus.CHUNKING: frozenset(
        {
            IngestionStatus.READY_FOR_INDEXING,
            IngestionStatus.READY_FOR_INDEXING_WITH_WARNING,
            IngestionStatus.QUEUED,
            IngestionStatus.FAILED,
        }
    ),
    IngestionStatus.READY_FOR_INDEXING: frozenset(
        {IngestionStatus.EMBEDDING, IngestionStatus.QUEUED, IngestionStatus.FAILED}
    ),
    IngestionStatus.READY_FOR_INDEXING_WITH_WARNING: frozenset(
        {IngestionStatus.EMBEDDING, IngestionStatus.QUEUED, IngestionStatus.FAILED}
    ),
    IngestionStatus.EMBEDDING: frozenset(
        {IngestionStatus.INDEXING, IngestionStatus.QUEUED, IngestionStatus.FAILED}
    ),
    IngestionStatus.INDEXING: frozenset(
        {
            IngestionStatus.COMPLETED,
            IngestionStatus.COMPLETED_WITH_WARNING,
            IngestionStatus.QUEUED,
            IngestionStatus.FAILED,
        }
    ),
    IngestionStatus.COMPLETED: frozenset({IngestionStatus.DELETING, IngestionStatus.QUEUED}),
    IngestionStatus.COMPLETED_WITH_WARNING: frozenset(
        {IngestionStatus.DELETING, IngestionStatus.QUEUED}
    ),
    IngestionStatus.FAILED: frozenset({IngestionStatus.DELETING, IngestionStatus.QUEUED}),
    IngestionStatus.DELETING: frozenset({IngestionStatus.DELETED}),
    IngestionStatus.DELETED: frozenset(),
}


@dataclass(frozen=True, slots=True)
class IngestionJob:
    id: UUID
    document_id: UUID
    status: IngestionStatus
    attempt_count: int = 0
    max_attempts: int = 3
    last_error: str | None = None
    last_error_category: str | None = None
    parse_warnings: tuple[ParseWarning | str, ...] = ()
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    started_at: datetime | None = None
    completed_at: datetime | None = None
    chunks_created: int = 0
    chunks_indexed: int = 0
    worker_id: str | None = None
    embedding_config_id: str | None = None

    def __post_init__(self) -> None:
        if self.attempt_count < 0 or self.max_attempts < 1:
            raise ValueError(
                "Ingestion attempts must be non-negative and max_attempts must be positive"
            )
        if self.chunks_created < 0 or self.chunks_indexed < 0:
            raise ValueError("Chunk counts must be non-negative")
        if self.chunks_indexed > self.chunks_created:
            raise ValueError("Indexed chunks cannot exceed created chunks")

    @classmethod
    def new(cls, document_id: UUID) -> "IngestionJob":
        return cls(id=uuid4(), document_id=document_id, status=IngestionStatus.QUEUED)

    @property
    def is_terminal(self) -> bool:
        return self.status.is_terminal

    @property
    def has_warnings(self) -> bool:
        return bool(self.parse_warnings) or self.status is IngestionStatus.COMPLETED_WITH_WARNING

    def transition_to(
        self, status: IngestionStatus, *, now: datetime | None = None
    ) -> "IngestionJob":
        self.status.transition_to(status)
        timestamp = now or datetime.now(UTC)
        return replace(
            self,
            status=status,
            started_at=self.started_at or timestamp if status.is_processing else self.started_at,
            completed_at=timestamp if status.is_terminal else None,
        )

    def with_progress(
        self,
        *,
        status: IngestionStatus | None = None,
        chunks_created: int | None = None,
        chunks_indexed: int | None = None,
        parse_warnings: tuple[ParseWarning | str, ...] | None = None,
        last_error: str | None = None,
    ) -> "IngestionJob":
        if status is not None and status is not self.status:
            self.status.transition_to(status)
        return replace(
            self,
            status=status or self.status,
            chunks_created=chunks_created if chunks_created is not None else self.chunks_created,
            chunks_indexed=chunks_indexed if chunks_indexed is not None else self.chunks_indexed,
            parse_warnings=parse_warnings if parse_warnings is not None else self.parse_warnings,
            last_error=last_error if last_error is not None else self.last_error,
        )
