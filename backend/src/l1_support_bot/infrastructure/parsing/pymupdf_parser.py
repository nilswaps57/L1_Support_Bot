"""PDF fallback parser using PyMuPDF."""

from __future__ import annotations

import io
from importlib import import_module
from typing import Any

from l1_support_bot.domain.errors import ProcessingError
from l1_support_bot.domain.models.document import FileType
from l1_support_bot.domain.models.parsed_document import (
    DocumentElement,
    ParsedDocument,
)

try:
    fitz: Any = import_module("fitz")
except ImportError:  # pragma: no cover
    fitz = None


class PyMuPDFParser:
    async def parse(self, content: bytes, file_type: FileType) -> ParsedDocument:
        return self._parse(content, file_type)

    def parse_sync(self, content: bytes, file_type: FileType) -> ParsedDocument:
        return self._parse(content, file_type)

    def _parse(self, content: bytes, file_type: FileType) -> ParsedDocument:
        if file_type is not FileType.PDF:
            raise ProcessingError("The PDF fallback cannot process this document type.")
        if fitz is None:
            raise ProcessingError(
                "The PDF fallback parser is unavailable.", details={"stage": "parsing"}
            )
        try:
            pdf = fitz.open(stream=io.BytesIO(content), filetype="pdf")
            elements: list[DocumentElement] = []
            for page_index, page in enumerate(pdf, start=1):
                text = page.get_text("text").strip()
                if text:
                    for block in (part.strip() for part in text.split("\n\n")):
                        if block:
                            elements.append(DocumentElement("paragraph", block, page_index))
            if not elements:
                raise ProcessingError(
                    "The PDF did not contain readable text.", details={"stage": "parsing"}
                )
            return ParsedDocument(tuple(elements), "pdf")
        except ProcessingError:
            raise
        except Exception as exc:
            raise ProcessingError(
                "The PDF could not be read.", details={"stage": "parsing"}
            ) from exc

    @staticmethod
    def make_test_pdf(text: str) -> bytes:
        if fitz is None:
            raise RuntimeError("PyMuPDF is required for PDF fixtures")
        document: Any = fitz.open()
        page = document.new_page()
        page.insert_text((72, 72), text)
        content = bytes(document.tobytes())
        document.close()
        return content
