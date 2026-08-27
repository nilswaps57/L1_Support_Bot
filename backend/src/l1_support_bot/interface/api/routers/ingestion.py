"""Ingestion progress and failure visibility routes."""

from uuid import UUID

from fastapi import APIRouter, Request

from l1_support_bot.domain.errors import ServiceUnavailableError
from l1_support_bot.interface.dependencies import get_dependencies
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
