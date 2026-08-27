"""Document upload and registry routes."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, File, Form, HTTPException, Query, Request, UploadFile, status

from l1_support_bot.application.ingestion.delete_document import DeleteDocument
from l1_support_bot.application.ingestion.get_document import GetDocument
from l1_support_bot.application.ingestion.get_documents import GetDocuments
from l1_support_bot.application.ingestion.upload_document import UploadDocument, UploadRequest
from l1_support_bot.domain.errors import ServiceUnavailableError
from l1_support_bot.domain.models.document import SourceType
from l1_support_bot.domain.models.ingestion import IngestionStatus
from l1_support_bot.domain.ports.file_storage import FileStoragePort
from l1_support_bot.domain.ports.repositories import DocumentRepository, IngestionJobRepository
from l1_support_bot.interface.dependencies import ensure_persistence_available, get_dependencies
from l1_support_bot.interface.dto.document_lifecycle import DocumentLifecycleResponse
from l1_support_bot.interface.dto.documents import (
    DocumentDetailResponse,
    DocumentListItem,
    DocumentListResponse,
    UploadAcceptedResponse,
)

router = APIRouter(prefix="/documents", tags=["documents"])


def _ports(
    request: Request,
) -> tuple[DocumentRepository, IngestionJobRepository, FileStoragePort]:
    dependencies = get_dependencies(request)
    if (
        dependencies.document_repository is None
        or dependencies.ingestion_job_repository is None
        or dependencies.file_storage is None
    ):
        raise ServiceUnavailableError("Document management is temporarily unavailable.")
    return (
        dependencies.document_repository,
        dependencies.ingestion_job_repository,
        dependencies.file_storage,
    )


@router.post("/upload", response_model=UploadAcceptedResponse, status_code=status.HTTP_202_ACCEPTED)
async def upload_document(
    request: Request,
    file: Annotated[UploadFile, File(...)],
    source_type: Annotated[str, Form(...)],
    name: Annotated[str | None, Form()] = None,
) -> UploadAcceptedResponse:
    await ensure_persistence_available(request)
    document_repository, ingestion_job_repository, file_storage = _ports(request)
    try:
        parsed_source_type = SourceType(source_type)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail="Invalid source_type") from exc
    settings = request.app.state.settings
    use_case = UploadDocument(
        document_repository=document_repository,
        ingestion_job_repository=ingestion_job_repository,
        file_storage=file_storage,
        max_size_bytes=settings.max_document_size_bytes,
    )
    document, job = await use_case.execute(
        UploadRequest(
            filename=file.filename or "",
            content_type=file.content_type,
            content=await file.read(),
            source_type=parsed_source_type,
            name=name,
        )
    )
    return UploadAcceptedResponse(
        document_id=document.id,
        job_id=job.id,
        status=document.status.value,
        name=document.name,
        file_type=document.file_type.value,
        file_size_bytes=document.file_size_bytes,
        checksum=document.checksum,
    )


@router.get("", response_model=DocumentListResponse)
async def list_documents(
    request: Request,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    cursor: Annotated[str | None, Query()] = None,
    status_filter: Annotated[IngestionStatus | None, Query(alias="status")] = None,
    source_type: Annotated[SourceType | None, Query()] = None,
) -> DocumentListResponse:
    document_repository, ingestion_job_repository, _ = _ports(request)
    result = await GetDocuments(
        document_repository=document_repository,
        ingestion_job_repository=ingestion_job_repository,
    ).execute(limit=limit, cursor=cursor, status=status_filter, source_type=source_type)
    return DocumentListResponse(
        items=[
            DocumentListItem.from_values(item.document, item.latest_job) for item in result.items
        ],
        total=result.total,
        limit=result.limit,
        next_cursor=result.next_cursor,
    )


@router.get("/{document_id}", response_model=DocumentDetailResponse)
async def get_document(request: Request, document_id: UUID) -> DocumentDetailResponse:
    document_repository, ingestion_job_repository, _ = _ports(request)
    result = await GetDocument(
        document_repository=document_repository,
        ingestion_job_repository=ingestion_job_repository,
    ).execute(document_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Document not found")
    return DocumentDetailResponse.from_values(result.document, result.latest_job)


@router.delete(
    "/{document_id}",
    response_model=DocumentLifecycleResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
async def delete_document(
    request: Request, document_id: UUID
) -> DocumentLifecycleResponse:
    await ensure_persistence_available(request)
    dependencies = get_dependencies(request)
    if dependencies.document_repository is None or dependencies.cleanup_document is None:
        raise ServiceUnavailableError("Document management is temporarily unavailable.")
    try:
        document = await DeleteDocument(
            documents=dependencies.document_repository,
            cleanup=dependencies.cleanup_document,
        ).execute(document_id)
    except LookupError as exc:
        raise HTTPException(status_code=404, detail="Document not found") from exc
    return DocumentLifecycleResponse(document_id=document.id, status=document.status.value)
