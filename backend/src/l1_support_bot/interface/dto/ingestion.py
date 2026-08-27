"""Public ingestion job status schemas."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from l1_support_bot.domain.models.ingestion import IngestionJob
from l1_support_bot.domain.models.parsed_document import ParseWarning


class IngestionWarningResponse(BaseModel):
    element_type: str = "UNKNOWN"
    description: str
    page_number: int | None = None
    code: str | None = None

    @classmethod
    def from_value(cls, warning: ParseWarning | str) -> "IngestionWarningResponse":
        if isinstance(warning, ParseWarning):
            return cls(
                element_type=warning.element_type,
                description=warning.description,
                page_number=warning.page_number,
                code=warning.code,
            )
        return cls(description=warning)


class IngestionJobResponse(BaseModel):
    job_id: UUID
    document_id: UUID
    status: str
    attempt_count: int
    chunks_created: int
    chunks_indexed: int
    started_at: datetime | None = None
    completed_at: datetime | None = None
    last_error: str | None = None
    last_error_category: str | None = None
    parse_warnings: list[IngestionWarningResponse] = Field(default_factory=list)

    @classmethod
    def from_job(cls, job: IngestionJob) -> "IngestionJobResponse":
        return cls(
            job_id=job.id,
            document_id=job.document_id,
            status=job.status.value,
            attempt_count=job.attempt_count,
            chunks_created=job.chunks_created,
            chunks_indexed=job.chunks_indexed,
            started_at=job.started_at,
            completed_at=job.completed_at,
            last_error=job.last_error,
            last_error_category=job.last_error_category,
            parse_warnings=[
                IngestionWarningResponse.from_value(warning) for warning in job.parse_warnings
            ],
        )
