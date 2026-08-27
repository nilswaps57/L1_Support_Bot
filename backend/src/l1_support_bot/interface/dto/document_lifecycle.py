"""Document deletion and re-indexing API schemas."""

from uuid import UUID

from pydantic import BaseModel


class DocumentLifecycleResponse(BaseModel):
    document_id: UUID
    status: str


class ReindexAcceptedResponse(BaseModel):
    document_id: UUID
    job_id: UUID
    status: str
