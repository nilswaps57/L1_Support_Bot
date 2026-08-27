from pathlib import Path

import pytest

from l1_support_bot.domain.errors import UnreadableFileError
from l1_support_bot.infrastructure.file_storage.local import LocalFileStorage


@pytest.mark.asyncio
async def test_storage_uses_safe_uuid_filename_and_verifies_checksum(tmp_path: Path) -> None:
    storage = LocalFileStorage(tmp_path)

    stored = await storage.store("../../manual.pdf", b"%PDF-1.7 source")

    assert Path(stored.storage_path).name == stored.storage_path
    assert stored.storage_path.endswith(".pdf")
    assert (tmp_path / stored.storage_path).read_bytes() == b"%PDF-1.7 source"
    assert stored.checksum


@pytest.mark.asyncio
async def test_storage_rejects_path_traversal_on_read_and_delete(tmp_path: Path) -> None:
    storage = LocalFileStorage(tmp_path)

    with pytest.raises(UnreadableFileError):
        await storage.read("../outside.pdf")
    with pytest.raises(UnreadableFileError):
        await storage.delete("../outside.pdf")


@pytest.mark.asyncio
async def test_storage_writes_atomically_and_cleans_up(tmp_path: Path) -> None:
    storage = LocalFileStorage(tmp_path)

    stored = await storage.store("manual.md", b"# title")
    assert not list(tmp_path.glob("*.tmp"))

    await storage.delete(stored.storage_path)
    assert not (tmp_path / stored.storage_path).exists()