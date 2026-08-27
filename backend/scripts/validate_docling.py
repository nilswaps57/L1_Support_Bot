"""Validate live Docling output against supplied representative documents."""

from __future__ import annotations

import argparse
import asyncio
import json
from pathlib import Path

from l1_support_bot.domain.models.document import FileType
from l1_support_bot.infrastructure.parsing.docling_parser import DoclingParser


async def validate(path: Path, max_pages: int) -> dict[str, object]:
    if not path.exists():
        raise FileNotFoundError(f"No validation document exists at {path}")
    if path.is_dir():
        files = sorted(
            item
            for item in path.iterdir()
            if item.suffix.lower() in {".pdf", ".docx", ".md"}
        )
        if not files:
            raise ValueError("No PDF, DOCX, or Markdown validation documents were found")
        return {"documents": [await validate(item, max_pages) for item in files]}
    file_type = {".pdf": FileType.PDF, ".docx": FileType.DOCX, ".md": FileType.MARKDOWN}.get(
        path.suffix.lower()
    )
    if file_type is None:
        raise ValueError("Validation input must be PDF, DOCX, or Markdown")
    parsed = await DoclingParser(validated=True).parse(path.read_bytes(), file_type)
    pages = {element.page_number for element in parsed.elements if element.page_number}
    return {
        "file": path.name,
        "source_format": parsed.source_format,
        "elements": len(parsed.elements),
        "headings": sum(element.element_type == "heading" for element in parsed.elements),
        "tables": sum(element.element_type == "table" for element in parsed.elements),
        "lists": sum(element.element_type == "list" for element in parsed.elements),
        "procedures": sum(element.element_type == "procedure" for element in parsed.elements),
        "pages_sampled": sorted(page for page in pages if page <= max_pages),
        "warnings": [warning.description for warning in parsed.warnings],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("path", type=Path)
    parser.add_argument("--max-pages", type=int, default=10)
    args = parser.parse_args()
    try:
        result = asyncio.run(validate(args.path, args.max_pages))
    except Exception as error:
        print(json.dumps({"status": "blocked", "reason": str(error)}))
        return 2
    print(json.dumps({"status": "passed", **result}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
