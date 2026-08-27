import io
import zipfile

import pytest

from l1_support_bot.application.ingestion.upload_document import UploadValidator
from l1_support_bot.domain.errors import (
    FileTooLargeError,
    UnreadableFileError,
    UnsupportedFileTypeError,
)
from l1_support_bot.domain.models.document import FileType


def docx_bytes() -> bytes:
    stream = io.BytesIO()
    with zipfile.ZipFile(stream, "w") as archive:
        archive.writestr("[Content_Types].xml", "types")
        archive.writestr("word/document.xml", "document")
    return stream.getvalue()


@pytest.mark.parametrize(
    ("filename", "content_type", "content", "file_type"),
    [
        ("manual.PDF", "application/pdf", b"%PDF-1.7 source", FileType.PDF),
        (
            "manual.docx",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            docx_bytes(),
            FileType.DOCX,
        ),
        ("manual.md", "text/markdown", b"# FLEXCUBE\n", FileType.MARKDOWN),
    ],
)
def test_accepts_supported_extensions_mime_types_and_signatures(
    filename: str, content_type: str, content: bytes, file_type: FileType
) -> None:
    result = UploadValidator(1024).validate(
        filename=filename, content_type=content_type, content=content
    )

    assert result.file_type is file_type
    assert len(result.checksum) == 64
    assert result.size_bytes == len(content)


def test_rejects_unsupported_extension() -> None:
    with pytest.raises(UnsupportedFileTypeError, match="Supported document formats"):
        UploadValidator(1024).validate(
            filename="manual.xlsx", content_type="application/octet-stream", content=b"data"
        )


def test_rejects_mismatched_mime_and_signature() -> None:
    with pytest.raises(UnsupportedFileTypeError):
        UploadValidator(1024).validate(
            filename="manual.pdf", content_type="text/plain", content=b"%PDF-1.7"
        )
    with pytest.raises(UnreadableFileError):
        UploadValidator(1024).validate(
            filename="manual.pdf", content_type="application/pdf", content=b"MZ executable"
        )


def test_rejects_empty_and_oversized_files() -> None:
    with pytest.raises(UnreadableFileError, match="empty"):
        UploadValidator(1024).validate(
            filename="manual.md", content_type="text/markdown", content=b""
        )
    with pytest.raises(FileTooLargeError) as error:
        UploadValidator(3).validate(
            filename="manual.md", content_type="text/markdown", content=b"four"
        )
    assert error.value.details["max_size_bytes"] == "3"


def test_rejects_malformed_docx_and_binary_markdown() -> None:
    with pytest.raises(UnreadableFileError):
        UploadValidator(1024).validate(
            filename="manual.docx",
            content_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            content=b"not a zip",
        )
    with pytest.raises(UnreadableFileError):
        UploadValidator(1024).validate(
            filename="manual.md", content_type="text/markdown", content=b"# title\x00"
        )