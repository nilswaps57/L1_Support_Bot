"""Application-owned metadata extraction contract."""

from collections.abc import Iterable
from typing import Protocol

from l1_support_bot.domain.models.parsed_document import DocumentElement, FlexcubeMetadata


class MetadataExtractorPort(Protocol):
    def extract(self, elements: Iterable[DocumentElement]) -> FlexcubeMetadata: ...
