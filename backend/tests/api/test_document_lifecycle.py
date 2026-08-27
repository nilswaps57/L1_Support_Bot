from dataclasses import dataclass
from uuid import UUID

import pytest
from fastapi.testclient import TestClient

from l1_support_bot.domain.errors import CleanupFailedError
from l1_support_bot.domain.models.document import Document, FileType, SourceType
from l1_support_bot.domain.models.ingestion import IngestionJob, IngestionStatus
from l1_support_bot.interface.api.main import create_app
from l1_support_bot.interface.config import Settings
from l1_support_bot.interface.dependencies import PortDependencies


def make_document(status: IngestionStatus) -> Document:
    document = Document.new(
        name="manual.md", original_filename="manual.md", file_type=FileType.MARKDOWN,
        source_type=SourceType.FLEXCUBE_MANUAL, checksum="d" * 64,
        storage_path="manual.md", file_size_bytes=4,
    ).transition_to(IngestionStatus.QUEUED)
    if status is not IngestionStatus.QUEUED:
        for transition in (
            IngestionStatus.PARSING,
            IngestionStatus.NORMALISING,
            IngestionStatus.CHUNKING,
            IngestionStatus.READY_FOR_INDEXING,
            IngestionStatus.EMBEDDING,
            IngestionStatus.INDEXING,
        ):
            document = document.transition_to(transition)
            if transition is status:
                return document
        document = document.transition_to(status)
    return document


@dataclass
class Documents:
    value: Document

    async def get(self, document_id: UUID):
        return self.value if document_id == self.value.id else None

    async def save(self, document: Document):
        self.value = document
        return document


@dataclass
class Jobs:
    value: IngestionJob

    async def latest_for_document(self, document_id: UUID):
        return self.value if self.value.document_id == document_id else None

    async def get(self, job_id: UUID):
        return self.value if self.value.id == job_id else None


class Cleanup:
    def __init__(self, error: Exception | None = None) -> None:
        self.error = error

    async def execute(self, document):
        if self.error:
            raise self.error
        return document.transition_to(IngestionStatus.DELETED)


class Reindex:
    async def execute(self, document_id: UUID):
        return IngestionJob.new(document_id).transition_to(IngestionStatus.PARSING)


@pytest.fixture
def lifecycle_api():
    document = make_document(IngestionStatus.COMPLETED)
    documents = Documents(document)
    jobs = Jobs(IngestionJob.new(document.id))
    dependencies = PortDependencies(
        document_repository=documents,
        ingestion_job_repository=jobs,
        cleanup_document=Cleanup(),
        reindex_document=Reindex(),
    )
    return TestClient(create_app(Settings(), dependencies=dependencies)), document, documents


def test_delete_returns_deleted_only_after_cleanup(lifecycle_api) -> None:
    client, document, _ = lifecycle_api

    response = client.delete(f"/api/v1/documents/{document.id}")

    assert response.status_code == 202
    assert response.json() == {"document_id": str(document.id), "status": "DELETED"}


def test_delete_active_ingestion_returns_conflict(lifecycle_api) -> None:
    _, document, _ = lifecycle_api
    document = make_document(IngestionStatus.EMBEDDING)
    lifecycle_api[2].value = document

    response = lifecycle_api[0].delete(f"/api/v1/documents/{document.id}")

    assert response.status_code == 409
    assert response.json()["error_code"] == "DOCUMENT_IN_PROCESSING"


def test_cleanup_failure_is_not_success(lifecycle_api) -> None:
    client, document, _ = lifecycle_api
    client.app.state.dependencies.cleanup_document = Cleanup(CleanupFailedError("cleanup failed"))

    response = client.delete(f"/api/v1/documents/{document.id}")

    assert response.status_code == 500
    assert response.json()["error_code"] == "DOCUMENT_CLEANUP_FAILED"


def test_reindex_returns_a_new_job(lifecycle_api) -> None:
    client, document, _ = lifecycle_api

    response = client.post(f"/api/v1/ingestion/{document.id}/reindex")

    assert response.status_code == 202
    assert response.json()["document_id"] == str(document.id)
    assert response.json()["status"] == "PARSING"
