"""Chunk parsed documents without crossing meaningful structure boundaries."""

from __future__ import annotations

from collections.abc import Sequence
from uuid import UUID, uuid4

from l1_support_bot.domain.models.chunk import ChunkMetadata, KnowledgeChunk
from l1_support_bot.domain.models.configuration import ChunkingConfig
from l1_support_bot.domain.models.parsed_document import DocumentElement, ParsedDocument
from l1_support_bot.infrastructure.parsing.flexcube_metadata_extractor import (
    FlexcubeMetadataExtractor,
)


class StructureAwareChunker:
    async def chunk(
        self,
        parsed_document: ParsedDocument,
        config: ChunkingConfig,
        *,
        document_id: UUID | None = None,
        ingestion_job_id: UUID | None = None,
    ) -> Sequence[KnowledgeChunk]:
        document_id = document_id or uuid4()
        ingestion_job_id = ingestion_job_id or uuid4()
        blocks = self._blocks(parsed_document.elements, config.target_chunk_tokens)
        chunks: list[KnowledgeChunk] = []
        previous_by_section: dict[tuple[str, ...], list[str]] = {}
        sequence = 0
        for section, element, text in blocks:
            words = text.split()
            start = 0
            while start < len(words):
                overlap = (
                    previous_by_section.get(section, [])
                    if start == 0
                    else words[max(0, start - config.overlap_tokens) : start]
                )
                available = config.max_chunk_tokens - len(overlap)
                part = words[start : start + available]
                combined = overlap + part
                chunk_text = " ".join(combined)
                metadata = self._metadata(parsed_document, element, section)
                chunks.append(
                    KnowledgeChunk.new(
                        document_id=document_id,
                        ingestion_job_id=ingestion_job_id,
                        sequence=sequence,
                        text=chunk_text,
                        metadata=metadata,
                    )
                )
                sequence += 1
                previous_by_section[section] = (
                    part[-config.overlap_tokens :] if config.overlap_tokens else []
                )
                start += len(part)
        return tuple(chunks)

    def _blocks(
        self, elements: tuple[DocumentElement, ...], max_tokens: int
    ) -> list[tuple[tuple[str, ...], DocumentElement, str]]:
        blocks: list[tuple[tuple[str, ...], DocumentElement, str]] = []
        current_section: tuple[str, ...] = ()
        current: list[str] = []
        current_element: DocumentElement | None = None

        def flush() -> None:
            nonlocal current, current_element
            if current and current_element is not None:
                blocks.append((current_section, current_element, " ".join(current)))
            current = []
            current_element = None

        for element in elements:
            section = element.section_path
            text = element.text.strip()
            atomic = element.element_type in {"table", "procedure", "list"}
            if section != current_section or atomic:
                flush()
                current_section = section
            if atomic:
                blocks.append((section, element, text))
                continue
            words = text.split()
            if current and len(current) + len(words) > max_tokens:
                flush()
            current_element = current_element or element
            current.extend(words)
        flush()
        return blocks

    def _metadata(
        self, document: ParsedDocument, element: DocumentElement, section: tuple[str, ...]
    ) -> ChunkMetadata:
        extracted = FlexcubeMetadataExtractor().extract((element,))
        source_metadata = document.metadata
        return ChunkMetadata(
            document_name=document.document_name or "Uploaded document",
            source_type=document.source_type,
            page_number=element.page_number,
            section=" > ".join(section) if section else None,
            task_code=(extracted.task_codes or source_metadata.task_codes or (None,))[0],
            screen_name=(extracted.screen_names or source_metadata.screen_names or (None,))[0],
            menu_path=(extracted.menu_paths or source_metadata.menu_paths or (None,))[0],
            prerequisites=extracted.prerequisites or source_metadata.prerequisites,
            modes=extracted.modes or source_metadata.modes,
            field_names=extracted.field_names or source_metadata.field_names,
            procedure_steps=element.procedure_steps
            or extracted.procedure_steps
            or source_metadata.procedure_steps,
            error_code=(extracted.error_codes or source_metadata.error_codes or (None,))[0],
            jira_id=(extracted.jira_ids or source_metadata.jira_ids or (None,))[0],
            rca_reference=(extracted.rca_references or source_metadata.rca_references or (None,))[
                0
            ],
            element_type=element.element_type,
        )
