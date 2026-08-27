"""Synthetic large-document regression checks; licensed manuals stay outside the repository."""

import tracemalloc
from time import perf_counter

import pytest

from l1_support_bot.domain.models.configuration import ChunkingConfig
from l1_support_bot.domain.models.parsed_document import DocumentElement, ParsedDocument
from l1_support_bot.infrastructure.chunking.structure_aware_chunker import StructureAwareChunker


@pytest.mark.integration
@pytest.mark.asyncio
async def test_synthetic_large_document_records_shape_and_memory_without_target_claims() -> None:
    elements = tuple(
        DocumentElement(
            element_type="paragraph",
            text=(f"Synthetic FLEXCUBE section {index} " + "operator guidance " * 40).strip(),
            section_path=(f"Section {index // 10}",),
        )
        for index in range(300)
    )
    document = ParsedDocument(
        elements=elements, source_format="synthetic", document_name="synthetic"
    )
    chunker = StructureAwareChunker()
    config = ChunkingConfig(target_chunk_tokens=128, min_chunk_tokens=16, max_chunk_tokens=256)

    tracemalloc.start()
    started = perf_counter()
    chunks = await chunker.chunk(document, config)
    elapsed_ms = (perf_counter() - started) * 1000
    _, peak_bytes = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    assert chunks
    assert len(chunks) <= len(elements)
    assert elapsed_ms >= 0
    assert peak_bytes > 0
