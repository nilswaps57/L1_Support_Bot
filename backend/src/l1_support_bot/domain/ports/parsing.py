"""Parser contract independent of a document-processing framework."""

from typing import Protocol

from l1_support_bot.domain.models.document import FileType
from l1_support_bot.domain.models.parsed_document import ParsedDocument


class ParserPort(Protocol):
    async def parse(self, content: bytes, file_type: FileType) -> ParsedDocument: ...


DocumentParserPort = ParserPort
