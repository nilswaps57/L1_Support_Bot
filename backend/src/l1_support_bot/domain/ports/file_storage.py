"""Safe source-file storage contract."""

from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True, slots=True)
class StoredFile:
    storage_path: str
    checksum: str
    file_size_bytes: int


class FileStoragePort(Protocol):
    async def store(self, original_filename: str, content: bytes) -> StoredFile: ...

    async def read(self, storage_path: str) -> bytes: ...

    async def delete(self, storage_path: str) -> None: ...
