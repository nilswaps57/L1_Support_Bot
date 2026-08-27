"""Ingestion progress and failure visibility routes."""

from uuid import UUID

from fastapi import APIRouter, HTTPException, Request, status

from l1_support_bot.domain.errors import ServiceUnavailableError
from l1_support_bot.interface.dependencies import ensure_persistence_available, get_dependencies
from l1_support_bot.interface.dto.document_lifecycle import ReindexAcceptedResponse
from l1_support_bot.interface.dto.ingestion import IngestionJobResponse

router = APIRouter(prefix="/ingestion", tags=["ingestion"])


@router.get("/jobs/{job_id}", response_model=IngestionJobResponse)
async def get_ingestion_job(request: Request, job_id: UUID) -> IngestionJobResponse:
    repository = get_dependencies(request).ingestion_job_repository
    if repository is None:
        raise ServiceUnavailableError("Ingestion status is temporarily unavailable.")
    job = await repository.get(job_id)
    if job is None:
        from fastapi import HTTPException

        raise HTTPException(status_code=404, detail="Ingestion job not found")
    return IngestionJobResponse.from_job(job)


@router.post(
    "/{document_id}/reindex",
    response_model=ReindexAcceptedResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
async def reindex_document(
    request: Request, document_id: UUID
) -> ReindexAcceptedResponse:
    await ensure_persistence_available(request)
    reindex = get_dependencies(request).reindex_document
    if reindex is None:
        raise ServiceUnavailableError("Document re-indexing is temporarily unavailable.")
    try:
        job = await reindex.execute(document_id)
    except LookupError as exc:
        raise HTTPException(status_code=404, detail="Document not found") from exc
    return ReindexAcceptedResponse(
        document_id=job.document_id,
        job_id=job.id,
        status=job.status.value,
    )
