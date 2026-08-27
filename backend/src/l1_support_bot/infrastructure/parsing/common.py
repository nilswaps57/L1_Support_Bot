"""Shared safe parser helpers."""

import re

from l1_support_bot.domain.models.parsed_document import DocumentElement, ParsedDocument


def parse_markdown(content: bytes, *, document_name: str = "") -> ParsedDocument:
    text = content.decode("utf-8")
    elements: list[DocumentElement] = []
    section_path: list[str] = []
    paragraph: list[str] = []
    list_items: list[str] = []

    def flush_paragraph() -> None:
        if paragraph:
            value = " ".join(paragraph).strip()
            elements.append(DocumentElement("paragraph", value, section_path=tuple(section_path)))
            paragraph.clear()

    def flush_list() -> None:
        if list_items:
            value = "\n".join(f"- {item}" for item in list_items)
            elements.append(
                DocumentElement(
                    "list", value, section_path=tuple(section_path), list_items=tuple(list_items)
                )
            )
            list_items.clear()

    for line in text.splitlines():
        heading = re.match(r"^(#{1,6})\s+(.+?)\s*$", line)
        item = re.match(r"^\s*(?:[-*+] |\d+[.)] )(.+?)\s*$", line)
        if heading:
            flush_paragraph()
            flush_list()
            level = len(heading.group(1))
            title = heading.group(2).strip()
            section_path[:] = section_path[: level - 1]
            section_path.append(title)
            elements.append(
                DocumentElement(
                    "heading", title, heading_level=level, section_path=tuple(section_path)
                )
            )
        elif item:
            flush_paragraph()
            list_items.append(item.group(1))
        elif line.strip():
            flush_list()
            paragraph.append(line.strip())
        else:
            flush_paragraph()
            flush_list()
    flush_paragraph()
    flush_list()
    return ParsedDocument(tuple(elements), "md", document_name)
