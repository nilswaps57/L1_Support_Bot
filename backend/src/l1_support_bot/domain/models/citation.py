"""Source citation value object."""

from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True, slots=True)
class Citation:
    chunk_id: UUID
    document_id: UUID
    document_name: str
    page_number: int | None = None
    section: str | None = None
    task_code: str | None = None
    screen_name: str | None = None
    error_code: str | None = None
    jira_id: str | None = None
    source_type: str | None = None
    relevance_score: float | None = None

    @property
    def identity(self) -> UUID:
        return self.chunk_id

    def __post_init__(self) -> None:
        if not self.document_name.strip():
            raise ValueError("Citation requires a document name")
        if self.page_number is not None and self.page_number < 1:
            raise ValueError("Citation page number must be positive")
        if self.relevance_score is not None and not 0 <= self.relevance_score <= 1:
            raise ValueError("Citation relevance score must be between zero and one")