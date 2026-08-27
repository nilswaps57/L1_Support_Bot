"""Docling-first parser adapter with a deterministic Markdown normalizer."""

from __future__ import annotations

import tempfile
from importlib import import_module
from typing import Any

from l1_support_bot.domain.errors import ProcessingError
from l1_support_bot.domain.models.document import FileType
from l1_support_bot.domain.models.parsed_document import (
    DocumentElement,
    ParsedDocument,
)
from l1_support_bot.infrastructure.parsing.common import parse_markdown


class DoclingParser:
    """Primary parser; the converter is imported only inside infrastructure."""

    def __init__(self, converter: Any | None = None, *, validated: bool = False) -> None:
        self.converter = converter
        self.validated = validated

    def parse_markdown(self, content: bytes) -> ParsedDocument:
        return parse_markdown(content)

    async def parse(self, content: bytes, file_type: FileType) -> ParsedDocument:
        if file_type is FileType.MARKDOWN:
            return self.parse_markdown(content)
        if not self.validated:
            raise ProcessingError(
                "The primary document parser requires live validation before indexing.",
                details={"stage": "parsing"},
            )
        if self.converter is None:
            try:
                converter_type = import_module("docling.document_converter").DocumentConverter
            except ImportError:
                raise ProcessingError(
                    "The primary document parser is unavailable.", details={"stage": "parsing"}
                ) from None
            self.converter = converter_type()
        suffix = ".pdf" if file_type is FileType.PDF else ".docx"
        try:
            with tempfile.NamedTemporaryFile(suffix=suffix) as source:
                source.write(content)
                source.flush()
                result = self.converter.convert(source.name)
            document = getattr(result, "document", result)
            return self._from_docling(document, file_type.value)
        except ProcessingError:
            raise
        except Exception as exc:
            raise ProcessingError(
                "The document could not be parsed.", details={"stage": "parsing"}
            ) from exc

    def _from_docling(self, document: Any, source_format: str) -> ParsedDocument:
        exported = document.export_to_dict() if hasattr(document, "export_to_dict") else document
        elements: list[DocumentElement] = []
        self._walk(exported, elements, ())
        if not elements and hasattr(document, "export_to_markdown"):
            return parse_markdown(document.export_to_markdown().encode(), document_name="")
        if not elements:
            raise ProcessingError(
                "The document did not contain readable content.", details={"stage": "parsing"}
            )
        return ParsedDocument(tuple(elements), source_format)

    def _walk(
        self, value: Any, output: list[DocumentElement], section_path: tuple[str, ...]
    ) -> None:
        if isinstance(value, list):
            for item in value:
                self._walk(item, output, section_path)
            return
        if not isinstance(value, dict):
            return
        raw_type = str(
            value.get("label") or value.get("type") or value.get("element_type") or "paragraph"
        ).lower()
        text = str(value.get("text") or value.get("content") or "").strip()
        current_path = section_path
        if raw_type in {"title", "heading", "section_header"} and text:
            current_path = section_path + (text,)
        page = self._page_number(value)
        if text:
            table_rows = self._table_rows(value) if "table" in raw_type else ()
            element_type = (
                "heading" if raw_type in {"title", "heading", "section_header"} else raw_type
            )
            output.append(
                DocumentElement(
                    element_type,
                    text,
                    page,
                    value.get("level"),
                    current_path,
                    table_rows=table_rows,
                )
            )
        for key, child in value.items():
            if key not in {"text", "content", "label", "type", "element_type", "prov", "level"}:
                self._walk(child, output, current_path)

    @staticmethod
    def _page_number(value: dict[str, Any]) -> int | None:
        provenance = value.get("prov") or value.get("provenance") or ()
        if isinstance(provenance, list) and provenance and isinstance(provenance[0], dict):
            raw = provenance[0].get("page_no") or provenance[0].get("page")
            return int(raw) if raw is not None else None
        return None

    @staticmethod
    def _table_rows(value: dict[str, Any]) -> tuple[tuple[str, ...], ...]:
        rows = value.get("data", {}).get("grid", []) if isinstance(value.get("data"), dict) else []
        result: list[tuple[str, ...]] = []
        for row in rows:
            if isinstance(row, list):
                result.append(
                    tuple(
                        str(cell.get("text", cell)) if isinstance(cell, dict) else str(cell)
                        for cell in row
                    )
                )
        return tuple(result)
