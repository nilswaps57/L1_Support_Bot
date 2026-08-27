"""Docling-first parser routing with approved format fallbacks."""

from l1_support_bot.domain.models.document import FileType
from l1_support_bot.domain.models.parsed_document import ParsedDocument, ParseWarning
from l1_support_bot.domain.ports.parsing import ParserPort


class FallbackParserRouter:
    def __init__(
        self, primary: ParserPort, pdf_fallback: ParserPort, docx_fallback: ParserPort
    ) -> None:
        self.primary = primary
        self.pdf_fallback = pdf_fallback
        self.docx_fallback = docx_fallback

    async def parse(self, content: bytes, file_type: FileType) -> ParsedDocument:
        try:
            return await self.primary.parse(content, file_type)
        except Exception:
            fallback = self.pdf_fallback if file_type is FileType.PDF else self.docx_fallback
            parsed = await fallback.parse(content, file_type)
            warning = ParseWarning(
                "parser",
                "The primary structured parser was unavailable; fallback parsing was used.",
                code="PRIMARY_PARSER_FALLBACK",
            )
            return parsed.__class__(
                parsed.elements,
                parsed.source_format,
                parsed.document_name,
                parsed.warnings + (warning,),
                parsed.metadata,
            )
