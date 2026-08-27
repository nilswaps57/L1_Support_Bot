"""Secure local filesystem implementation for source documents."""

from __future__ import annotations

import hashlib
import os
from pathlib import Path, PurePath
from uuid import uuid4

from l1_support_bot.domain.errors import UnreadableFileError
from l1_support_bot.domain.ports.file_storage import FileStoragePort, StoredFile


class LocalFileStorage(FileStoragePort):
    def __init__(self, root: str | Path) -> None:
        self.root = Path(root).expanduser().resolve()
        self.root.mkdir(parents=True, exist_ok=True)

    async def store(self, original_filename: str, content: bytes) -> StoredFile:
        suffix = PurePath(original_filename).suffix.lower()
        if suffix not in {".pdf", ".docx", ".md"}:
            raise UnreadableFileError("The source filename has an unsupported extension.")
        relative_path = Path(f"{uuid4()}{suffix}")
        destination = self._resolve_safe(relative_path)
        temporary = self.root / f".{uuid4()}.tmp"
        checksum = hashlib.sha256(content).hexdigest()
        try:
            temporary.write_bytes(content)
            os.replace(temporary, destination)
        except OSError as exc:
            temporary.unlink(missing_ok=True)
            raise UnreadableFileError("The document could not be stored locally.") from exc
        return StoredFile(str(relative_path), checksum, len(content))

    async def read(self, storage_path: str) -> bytes:
        try:
            return self._resolve_safe(storage_path).read_bytes()
        except (OSError, ValueError) as exc:
            raise UnreadableFileError("The document could not be read from local storage.") from exc

    async def delete(self, storage_path: str) -> None:
        try:
            self._resolve_safe(storage_path).unlink(missing_ok=True)
        except (OSError, ValueError) as exc:
            raise UnreadableFileError(
                "The document could not be removed from local storage."
            ) from exc

    def _resolve_safe(self, storage_path: str | Path) -> Path:
        candidate = (self.root / storage_path).resolve()
        try:
            candidate.relative_to(self.root)
        except ValueError as exc:
            raise ValueError("Storage path escapes the configured root") from exc
        return candidate