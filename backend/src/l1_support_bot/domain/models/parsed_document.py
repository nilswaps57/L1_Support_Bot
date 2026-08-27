"""Parser-independent document structure and diagnostics."""

from collections.abc import Mapping
from dataclasses import dataclass
from types import MappingProxyType


@dataclass(frozen=True, slots=True)
class ParseWarning:
    element_type: str
    description: str
    page_number: int | None = None
    code: str | None = None

    def __post_init__(self) -> None:
        if not self.description.strip():
            raise ValueError("Parse warning description cannot be empty")
        if self.page_number is not None and self.page_number < 1:
            raise ValueError("Parse warning page number must be positive")


@dataclass(frozen=True, slots=True)
class DocumentElement:
    element_type: str
    text: str
    page_number: int | None = None
    heading_level: int | None = None
    section_path: tuple[str, ...] = ()
    list_items: tuple[str, ...] = ()
    table_rows: tuple[tuple[str, ...], ...] = ()
    procedure_steps: tuple[str, ...] = ()
    metadata: Mapping[str, str] = MappingProxyType({})

    def __post_init__(self) -> None:
        if not self.element_type.strip():
            raise ValueError("Document elements require a type")
        if not self.text.strip():
            raise ValueError("Document elements require text")
        if self.page_number is not None and self.page_number < 1:
            raise ValueError("Document element page number must be positive")
        if self.heading_level is not None and self.heading_level < 1:
            raise ValueError("Heading level must be positive")


@dataclass(frozen=True, slots=True)
class FlexcubeMetadata:
    task_codes: tuple[str, ...] = ()
    screen_names: tuple[str, ...] = ()
    menu_paths: tuple[str, ...] = ()
    prerequisites: tuple[str, ...] = ()
    modes: tuple[str, ...] = ()
    field_names: tuple[str, ...] = ()
    procedure_steps: tuple[str, ...] = ()
    error_codes: tuple[str, ...] = ()
    jira_ids: tuple[str, ...] = ()
    rca_references: tuple[str, ...] = ()
    diagnostics: tuple[ParseWarning, ...] = ()


@dataclass(frozen=True, slots=True)
class ParsedDocument:
    elements: tuple[DocumentElement, ...]
    source_format: str = "unknown"
    document_name: str = ""
    warnings: tuple[ParseWarning, ...] = ()
    metadata: FlexcubeMetadata = FlexcubeMetadata()
    source_type: str | None = None

    def __post_init__(self) -> None:
        if not self.source_format.strip():
            raise ValueError("Parsed documents require a source format")

    @property
    def text(self) -> str:
        return "\n\n".join(element.text for element in self.elements)

    @property
    def all_warnings(self) -> tuple[ParseWarning, ...]:
        return self.warnings + self.metadata.diagnostics
