import asyncio
from dataclasses import dataclass, field
from uuid import UUID

import pytest

from l1_support_bot.application.ingestion.upload_document import UploadDocument, UploadRequest
from l1_support_bot.domain.errors import DuplicateDocumentError
from l1_support_bot.domain.models.document import Document, SourceType
from l1_support_bot.domain.models.ingestion import IngestionJob
from l1_support_bot.domain.ports.file_storage import StoredFile


@dataclass
class InMemoryDocuments:
    documents: dict[UUID, Document] = field(default_factory=dict)

    async def get(self, document_id: UUID) -> Document | None:
        return self.documents.get(document_id)

    async def get_by_checksum(self, checksum: str) -> Document | None:
        return next(
            (document for document in self.documents.values() if document.checksum == checksum),
            None,
        )

    async def save(self, document: Document) -> Document:
        if await self.get_by_checksum(document.checksum) is not None:
            raise DuplicateDocumentError("Duplicate")
        self.documents[document.id] = document
        return document

    async def list(self, *, status=None, source_type=None):
        return tuple(self.documents.values())

    async def update_status(self, document_id, status):
        raise NotImplementedError

    async def delete(self, document_id):
        self.documents.pop(document_id, None)


@dataclass
class InMemoryJobs:
    jobs: list[IngestionJob] = field(default_factory=list)

    async def create(self, job: IngestionJob) -> IngestionJob:
        self.jobs.append(job)
        return job

    async def get(self, job_id):
        return next((job for job in self.jobs if job.id == job_id), None)

    async def update(self, job):
        return job

    async def list_pending(self, *, limit=10):
        return tuple(self.jobs[:limit])

    async def latest_for_document(self, document_id):
        return next((job for job in reversed(self.jobs) if job.document_id == document_id), None)


class FakeStorage:
    def __init__(self) -> None:
        self.files: dict[str, bytes] = {}

    async def store(self, original_filename: str, content: bytes) -> StoredFile:
        path = f"{len(self.files)}.pdf"
        self.files[path] = content
        from hashlib import sha256

        return StoredFile(path, sha256(content).hexdigest(), len(content))

    async def read(self, storage_path: str) -> bytes:
        return self.files[storage_path]

    async def delete(self, storage_path: str) -> None:
        self.files.pop(storage_path, None)


def request() -> UploadRequest:
    return UploadRequest(
        filename="manual.pdf",
        content_type="application/pdf",
        content=b"%PDF-1.7 same source",
        source_type=SourceType.FLEXCUBE_MANUAL,
    )


@pytest.mark.asyncio
async def test_duplicate_checksum_is_rejected_before_storage() -> None:
    documents = InMemoryDocuments()
    storage = FakeStorage()
    use_case = UploadDocument(
        document_repository=documents,
        ingestion_job_repository=InMemoryJobs(),
        file_storage=storage,
        max_size_bytes=1024,
    )
    await use_case.execute(request())

    with pytest.raises(DuplicateDocumentError):
        await use_case.execute(request())
    assert len(storage.files) == 1


@pytest.mark.asyncio
async def test_concurrent_identical_uploads_leave_one_registration() -> None:
    documents = InMemoryDocuments()
    jobs = InMemoryJobs()
    use_case = UploadDocument(
        document_repository=documents,
        ingestion_job_repository=jobs,
        file_storage=FakeStorage(),
        max_size_bytes=1024,
    )
    results = await asyncio.gather(
        use_case.execute(request()), use_case.execute(request()), return_exceptions=True
    )

    assert sum(isinstance(result, tuple) for result in results) == 1
    assert sum(isinstance(result, DuplicateDocumentError) for result in results) == 1
    assert len(documents.documents) == 1
    assert len(jobs.jobs) == 1