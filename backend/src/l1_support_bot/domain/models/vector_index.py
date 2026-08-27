"""Vector-index payload models independent of storage infrastructure."""

from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True, slots=True)
class VectorPayload:
    chunk_id: UUID
    document_id: UUID
    ingestion_job_id: UUID
    document_name: str
    text: str
    embedding_model_id: str
    page_number: int | None = None
    section: str | None = None
    task_code: str | None = None
    screen_name: str | None = None
    error_code: str | None = None
    jira_id: str | None = None
    source_type: str | None = None

    def __post_init__(self) -> None:
        if not self.document_name.strip() or not self.text.strip():
            raise ValueError("Vector payload requires source text and document name")
        if not self.embedding_model_id.strip():
            raise ValueError("Vector payload requires embedding compatibility identity")
