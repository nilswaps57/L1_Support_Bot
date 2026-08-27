from dataclasses import dataclass, field
from uuid import UUID

import pytest
from fastapi.testclient import TestClient

from l1_support_bot.domain.errors import DuplicateDocumentError
from l1_support_bot.domain.models.document import Document
from l1_support_bot.domain.models.ingestion import IngestionJob
from l1_support_bot.domain.ports.file_storage import StoredFile
from l1_support_bot.interface.api.main import create_app
from l1_support_bot.interface.config import Settings
from l1_support_bot.interface.dependencies import PortDependencies


@dataclass
class Documents:
    values: dict[UUID, Document] = field(default_factory=dict)

    async def get(self, document_id: UUID) -> Document | None:
        return self.values.get(document_id)

    async def get_by_checksum(self, checksum: str) -> Document | None:
        return next((item for item in self.values.values() if item.checksum == checksum), None)

    async def save(self, document: Document) -> Document:
        if await self.get_by_checksum(document.checksum) is not None:
            raise DuplicateDocumentError("Duplicate")
        self.values[document.id] = document
        return document

    async def list(self, *, status=None, source_type=None):
        return tuple(
            item
            for item in self.values.values()
            if (status is None or item.status is status)
            and (source_type is None or item.source_type is source_type)
        )

    async def update_status(self, document_id, status):
        raise NotImplementedError

    async def delete(self, document_id):
        self.values.pop(document_id, None)


@dataclass
class Jobs:
    values: list[IngestionJob] = field(default_factory=list)

    async def create(self, job: IngestionJob) -> IngestionJob:
        self.values.append(job)
        return job

    async def get(self, job_id):
        return next((item for item in self.values if item.id == job_id), None)

    async def update(self, job):
        return job

    async def list_pending(self, *, limit=10):
        return tuple(self.values[:limit])

    async def latest_for_document(self, document_id):
        return next(
            (item for item in reversed(self.values) if item.document_id == document_id), None
        )


class Storage:
    def __init__(self) -> None:
        self.values: dict[str, bytes] = {}

    async def store(self, original_filename: str, content: bytes) -> StoredFile:
        from hashlib import sha256

        path = f"{len(self.values)}.pdf"
        self.values[path] = content
        return StoredFile(path, sha256(content).hexdigest(), len(content))

    async def read(self, storage_path: str) -> bytes:
        return self.values[storage_path]

    async def delete(self, storage_path: str) -> None:
        self.values.pop(storage_path, None)


@pytest.fixture
def api() -> tuple[TestClient, Documents, Jobs, Storage]:
    documents = Documents()
    jobs = Jobs()
    storage = Storage()
    settings = Settings(max_document_size_bytes=100)
    app = create_app(
        settings=settings,
        dependencies=PortDependencies(
            document_repository=documents,
            ingestion_job_repository=jobs,
            file_storage=storage,
        ),
    )
    return TestClient(app), documents, jobs, storage


def test_valid_upload_returns_202_and_registers_queued_job(api) -> None:
    client, documents, jobs, storage = api

    response = client.post(
        "/api/v1/documents/upload",
        files={"file": ("manual.pdf", b"%PDF-1.7 source", "application/pdf")},
        data={"source_type": "flexcube_manual"},
    )

    assert response.status_code == 202
    payload = response.json()
    assert payload["status"] == "QUEUED"
    assert UUID(payload["document_id"]) in documents.values
    assert len(jobs.values) == 1
    assert len(storage.values) == 1


def test_invalid_and_duplicate_uploads_leave_registry_unchanged(api) -> None:
    client, documents, jobs, storage = api
    valid = {
        "files": {"file": ("manual.pdf", b"%PDF-1.7 source", "application/pdf")},
        "data": {"source_type": "flexcube_manual"},
    }
    assert client.post("/api/v1/documents/upload", **valid).status_code == 202
    before = (len(documents.values), len(jobs.values), len(storage.values))

    duplicate = client.post("/api/v1/documents/upload", **valid)
    unsupported = client.post(
        "/api/v1/documents/upload",
        files={"file": ("manual.xlsx", b"data", "application/octet-stream")},
        data={"source_type": "other"},
    )

    assert duplicate.status_code == 409
    assert duplicate.json()["error_code"] == "DUPLICATE_DOCUMENT"
    assert unsupported.status_code == 400
    assert unsupported.json()["error_code"] == "UNSUPPORTED_FILE_TYPE"
    assert (len(documents.values), len(jobs.values), len(storage.values)) == before


def test_list_and_detail_return_document_and_latest_job(api) -> None:
    client, _, _, _ = api
    uploaded = client.post(
        "/api/v1/documents/upload",
        files={"file": ("manual.md", b"# FLEXCUBE", "text/markdown")},
        data={"source_type": "other", "name": "Support manual"},
    )
    document_id = uploaded.json()["document_id"]

    listing = client.get("/api/v1/documents")
    detail = client.get(f"/api/v1/documents/{document_id}")

    assert listing.status_code == 200
    assert listing.json()["items"][0]["name"] == "Support manual"
    assert detail.status_code == 200
    assert detail.json()["latest_job"]["status"] == "QUEUED"
    assert detail.json()["checksum"]


def test_missing_multipart_file_is_rejected(api) -> None:
    client, _, _, _ = api

    response = client.post(
        "/api/v1/documents/upload", data={"source_type": "other"}
    )

    assert response.status_code == 422
    assert response.json()["error_code"] == "VALIDATION_ERROR"