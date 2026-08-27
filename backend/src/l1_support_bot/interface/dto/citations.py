"""Public citation response schema."""

from uuid import UUID

from pydantic import BaseModel


class CitationResponse(BaseModel):
    chunk_id: UUID
    document_id: UUID
    document_name: str
    page_number: int | None = None
    section: str | None = None
    task_code: str | None = None
    screen_name: str | None = None
    menu_path: str | None = None
    prerequisites: tuple[str, ...] = ()
    modes: tuple[str, ...] = ()
    field_names: tuple[str, ...] = ()
    procedure_steps: tuple[str, ...] = ()
    error_code: str | None = None
    jira_id: str | None = None
    rca_reference: str | None = None
    source_type: str | None = None
    relevance_score: float | None = None