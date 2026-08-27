"""Validate, store, and register an uploaded source document."""

from __future__ import annotations

import hashlib
import io
import zipfile
from asyncio import Lock
from dataclasses import dataclass
from pathlib import PurePath
from typing import Final

from l1_support_bot.domain.errors import (
    DuplicateDocumentError,
    FileTooLargeError,
    UnreadableFileError,
    UnsupportedFileTypeError,
)
from l1_support_bot.domain.models.document import Document, FileType, SourceType
from l1_support_bot.domain.models.ingestion import IngestionJob, IngestionStatus
from l1_support_bot.domain.ports.file_storage import FileStoragePort
from l1_support_bot.domain.ports.repositories import DocumentRepository, IngestionJobRepository


@dataclass(frozen=True, slots=True)
class UploadRequest:
    filename: str
    content_type: str | None
    content: bytes
    source_type: SourceType
    name: str | None = None
    description: str | None = None


@dataclass(frozen=True, slots=True)
class ValidatedUpload:
    file_type: FileType
    checksum: str
    size_bytes: int


class UploadValidator:
    _MIME_TYPES: Final[dict[FileType, frozenset[str]]] = {
        FileType.PDF: frozenset({"application/pdf"}),
        FileType.DOCX: frozenset(
            {"application/vnd.openxmlformats-officedocument.wordprocessingml.document"}
        ),
        FileType.MARKDOWN: frozenset({"text/markdown", "text/plain"}),
    }

    def __init__(self, max_size_bytes: int) -> None:
        if max_size_bytes <= 0:
            raise ValueError("Maximum document size must be positive")
        self.max_size_bytes = max_size_bytes

    def validate(
        self, *, filename: str, content_type: str | None, content: bytes
    ) -> ValidatedUpload:
        suffix = PurePath(filename).suffix.lower()
        file_type = {".pdf": FileType.PDF, ".docx": FileType.DOCX, ".md": FileType.MARKDOWN}.get(
            suffix
        )
        if file_type is None:
            raise UnsupportedFileTypeError(
                "Supported document formats are PDF, DOCX, and Markdown.",
                details={"supported_extensions": ".pdf, .docx, .md"},
            )
        if len(content) == 0:
            raise UnreadableFileError("The uploaded document is empty.")
        if len(content) > self.max_size_bytes:
            raise FileTooLargeError(
                "The uploaded document exceeds the configured size limit.",
                details={"max_size_bytes": str(self.max_size_bytes)},
            )
        if content_type not in self._MIME_TYPES[file_type]:
            raise UnsupportedFileTypeError(
                "The uploaded file MIME type does not match its extension.",
                details={"expected_file_type": file_type.value},
            )
        if not self._signature_matches(file_type, content):
            raise UnreadableFileError(
                "The uploaded file content does not match its declared format.",
                details={"file_type": file_type.value},
            )
        return ValidatedUpload(
            file_type=file_type,
            checksum=hashlib.sha256(content).hexdigest(),
            size_bytes=len(content),
        )

    @staticmethod
    def _signature_matches(file_type: FileType, content: bytes) -> bool:
        if file_type is FileType.PDF:
            return content.startswith(b"%PDF-")
        if file_type is FileType.DOCX:
            try:
                with zipfile.ZipFile(io.BytesIO(content)) as archive:
                    names = set(archive.namelist())
            except (OSError, zipfile.BadZipFile):
                return False
            return "[Content_Types].xml" in names and "word/document.xml" in names
        try:
            decoded = content.decode("utf-8")
        except UnicodeDecodeError:
            return False
        return "\x00" not in decoded


class UploadDocument:
    def __init__(
        self,
        *,
        document_repository: DocumentRepository,
        ingestion_job_repository: IngestionJobRepository,
        file_storage: FileStoragePort,
        max_size_bytes: int,
    ) -> None:
        self.document_repository = document_repository
        self.ingestion_job_repository = ingestion_job_repository
        self.file_storage = file_storage
        self.validator = UploadValidator(max_size_bytes)
        self._upload_lock = Lock()

    async def execute(self, request: UploadRequest) -> tuple[Document, IngestionJob]:
        async with self._upload_lock:
            return await self._execute(request)

    async def _execute(self, request: UploadRequest) -> tuple[Document, IngestionJob]:
        validated = self.validator.validate(
                filename=request.filename,
                content_type=request.content_type,
                content=request.content,
            )
        existing = await self.document_repository.get_by_checksum(validated.checksum)
        if existing is not None and existing.status is not IngestionStatus.DELETED:
            raise DuplicateDocumentError(
                "A document with identical content is already registered.",
                details={"existing_document_id": str(existing.id)},
            )

        stored = await self.file_storage.store(request.filename, request.content)
        if stored.checksum != validated.checksum or stored.file_size_bytes != validated.size_bytes:
            await self.file_storage.delete(stored.storage_path)
            raise UnreadableFileError("The stored document failed integrity verification.")

        document = Document.new(
            name=request.name or request.filename,
            original_filename=request.filename,
            file_type=validated.file_type,
            source_type=request.source_type,
            checksum=validated.checksum,
            storage_path=stored.storage_path,
            file_size_bytes=validated.size_bytes,
            description=request.description,
        ).transition_to(IngestionStatus.QUEUED)
        job = IngestionJob.new(document.id)
        try:
            saved_document = await self.document_repository.save(document)
            saved_job = await self.ingestion_job_repository.create(job)
        except Exception:
            await self.file_storage.delete(stored.storage_path)
            raise
        return saved_document, saved_job