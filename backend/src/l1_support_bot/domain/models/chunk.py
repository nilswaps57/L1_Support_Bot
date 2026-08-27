"""Knowledge chunk and source metadata value objects."""

from dataclasses import dataclass
from uuid import UUID, uuid4


@dataclass(frozen=True, slots=True)
class ChunkMetadata:
    document_name: str
    source_type: str | None = None
    page_number: int | None = None
    section: str | None = None
    task_code: str | None = None
    screen_name: str | None = None
    module: str | None = None
    functional_area: str | None = None
    menu_path: str | None = None
    prerequisites: tuple[str, ...] = ()
    modes: tuple[str, ...] = ()
    field_names: tuple[str, ...] = ()
    procedure_steps: tuple[str, ...] = ()
    error_code: str | None = None
    jira_id: str | None = None
    rca_reference: str | None = None
    element_type: str = "paragraph"

    def __post_init__(self) -> None:
        if not self.document_name.strip():
            raise ValueError("Chunk metadata requires a document name")
        if self.page_number is not None and self.page_number < 1:
            raise ValueError("Page number must be positive")


@dataclass(frozen=True, slots=True)
class KnowledgeChunk:
    id: UUID
    document_id: UUID
    ingestion_job_id: UUID
    sequence: int
    text: str
    metadata: ChunkMetadata
    embedding_model_id: str | None = None

    def __post_init__(self) -> None:
        if self.sequence < 0:
            raise ValueError("Chunk sequence must be non-negative")
        if not self.text.strip():
            raise ValueError("Knowledge chunk text cannot be empty")

    @classmethod
    def new(
        cls,
        *,
        document_id: UUID,
        ingestion_job_id: UUID,
        sequence: int,
        text: str,
        metadata: ChunkMetadata,
        embedding_model_id: str | None = None,
    ) -> "KnowledgeChunk":
        return cls(
            uuid4(), document_id, ingestion_job_id, sequence, text, metadata, embedding_model_id
        )