"""Framework-independent knowledge document entity."""

import re
from dataclasses import dataclass, replace
from datetime import UTC, datetime
from enum import StrEnum
from uuid import UUID, uuid4

from l1_support_bot.domain.models.ingestion import IngestionStatus


class FileType(StrEnum):
    PDF = "pdf"
    DOCX = "docx"
    MARKDOWN = "md"


class SourceType(StrEnum):
    FLEXCUBE_MANUAL = "flexcube_manual"
    RCA = "rca"
    JIRA_EXPORT = "jira_export"
    PROCEDURE = "procedure"
    OTHER = "other"


@dataclass(frozen=True, slots=True)
class Document:
    id: UUID
    name: str
    original_filename: str
    file_type: FileType
    source_type: SourceType
    checksum: str
    storage_path: str
    file_size_bytes: int
    status: IngestionStatus
    uploaded_at: datetime
    updated_at: datetime
    description: str | None = None

    def __post_init__(self) -> None:
        if not self.name.strip() or not self.original_filename.strip():
            raise ValueError("Document names cannot be empty")
        if self.file_size_bytes <= 0:
            raise ValueError("Document size must be positive")
        if re.fullmatch(r"[0-9a-f]{64}", self.checksum) is None:
            raise ValueError("Document checksum must be a SHA-256 hex digest")
        if not self.storage_path or ".." in self.storage_path.split("/"):
            raise ValueError("Document storage path must be relative and safe")

    @classmethod
    def new(
        cls,
        *,
        name: str,
        original_filename: str,
        file_type: FileType,
        source_type: SourceType,
        checksum: str,
        storage_path: str,
        file_size_bytes: int,
        description: str | None = None,
    ) -> "Document":
        now = datetime.now(UTC)
        return cls(
            id=uuid4(),
            name=name,
            original_filename=original_filename,
            file_type=file_type,
            source_type=source_type,
            checksum=checksum,
            storage_path=storage_path,
            file_size_bytes=file_size_bytes,
            status=IngestionStatus.UPLOADED,
            uploaded_at=now,
            updated_at=now,
            description=description,
        )

    def transition_to(self, status: IngestionStatus, *, now: datetime | None = None) -> "Document":
        self.status.transition_to(status)
        return replace(self, status=status, updated_at=now or datetime.now(UTC))