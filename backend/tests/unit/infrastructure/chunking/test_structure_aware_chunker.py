import pytest

from l1_support_bot.domain.models.configuration import ChunkingConfig
from l1_support_bot.domain.models.parsed_document import DocumentElement, ParsedDocument
from l1_support_bot.infrastructure.chunking.structure_aware_chunker import StructureAwareChunker


@pytest.mark.asyncio
async def test_chunker_keeps_sections_and_procedures_together_and_overlaps_text() -> None:
    document = ParsedDocument(
        elements=(
            DocumentElement(element_type="heading", text="BA435", section_path=("BA435",)),
            DocumentElement(
                element_type="procedure",
                text="Step 1 open screen. Step 2 authorize.",
                section_path=("BA435",),
            ),
            DocumentElement(
                element_type="table",
                text="Field | Value\nCustomer | Required",
                section_path=("BA435",),
            ),
            DocumentElement(
                element_type="paragraph",
                text="Additional guidance for operators.",
                section_path=("BA435",),
            ),
            DocumentElement(element_type="heading", text="BA436", section_path=("BA436",)),
            DocumentElement(
                element_type="paragraph", text="A separate task.", section_path=("BA436",)
            ),
        )
    )

    chunks = await StructureAwareChunker().chunk(
        document,
        ChunkingConfig(
            target_chunk_tokens=8, min_chunk_tokens=1, max_chunk_tokens=12, overlap_tokens=2
        ),
    )

    assert len(chunks) >= 2
    assert all(chunk.metadata.section for chunk in chunks)
    assert any(chunk.metadata.element_type == "table" for chunk in chunks)
    assert any(chunk.metadata.element_type == "procedure" for chunk in chunks)
    assert all(len(chunk.text.split()) <= 12 for chunk in chunks)
    assert chunks[-1].metadata.section != chunks[0].metadata.section


def test_chunker_rejects_invalid_overlap_configuration() -> None:
    with pytest.raises(ValueError):
        ChunkingConfig(
            target_chunk_tokens=8, min_chunk_tokens=1, max_chunk_tokens=12, overlap_tokens=12
        )
