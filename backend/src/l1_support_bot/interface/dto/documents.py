"""Public document API schemas."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from l1_support_bot.domain.models.document import Document
from l1_support_bot.domain.models.ingestion import IngestionJob
from l1_support_bot.interface.dto.ingestion import IngestionWarningResponse


class UploadAcceptedResponse(BaseModel):
    document_id: UUID
    job_id: UUID
    status: str
    name: str
    file_type: str
    file_size_bytes: int
    checksum: str


class DocumentListItem(BaseModel):
    document_id: UUID
    name: str
    file_type: str
    source_type: str
    status: str
    file_size_bytes: int
    chunks_indexed: int = 0
    uploaded_at: datetime
    updated_at: datetime

    @classmethod
    def from_values(cls, document: Document, job: IngestionJob | None) -> "DocumentListItem":
        return cls(
            document_id=document.id,
            name=document.name,
            file_type=document.file_type.value,
            source_type=document.source_type.value,
            status=document.status.value,
            file_size_bytes=document.file_size_bytes,
            chunks_indexed=job.chunks_indexed if job else 0,
            uploaded_at=document.uploaded_at,
            updated_at=document.updated_at,
        )


class DocumentListResponse(BaseModel):
    items: list[DocumentListItem]
    total: int
    limit: int
    next_cursor: str | None = None


class ParseWarningResponse(BaseModel):
    element_type: str = "UNKNOWN"
    description: str


class LatestJobResponse(BaseModel):
    job_id: UUID
    status: str
    chunks_created: int
    chunks_indexed: int
    parse_warnings: list[IngestionWarningResponse] = Field(default_factory=list)

    @classmethod
    def from_job(cls, job: IngestionJob) -> "LatestJobResponse":
        return cls(
            job_id=job.id,
            status=job.status.value,
            chunks_created=job.chunks_created,
            chunks_indexed=job.chunks_indexed,
            parse_warnings=[
                IngestionWarningResponse.from_value(warning) for warning in job.parse_warnings
            ],
        )


class DocumentDetailResponse(BaseModel):
    document_id: UUID
    name: str
    original_filename: str
    file_type: str
    source_type: str
    status: str
    file_size_bytes: int
    checksum: str
    uploaded_at: datetime
    updated_at: datetime
    description: str | None = None
    chunks_created: int = 0
    chunks_indexed: int = 0
    latest_job: LatestJobResponse | None = None

    @classmethod
    def from_values(cls, document: Document, job: IngestionJob | None) -> "DocumentDetailResponse":
        return cls(
            document_id=document.id,
            name=document.name,
            original_filename=document.original_filename,
            file_type=document.file_type.value,
            source_type=document.source_type.value,
            status=document.status.value,
            file_size_bytes=document.file_size_bytes,
            checksum=document.checksum,
            uploaded_at=document.uploaded_at,
            updated_at=document.updated_at,
            description=document.description,
            chunks_created=job.chunks_created if job else 0,
            chunks_indexed=job.chunks_indexed if job else 0,
            latest_job=LatestJobResponse.from_job(job) if job else None,
        )
