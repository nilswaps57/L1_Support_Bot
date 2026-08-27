import re
from uuid import uuid4

from l1_support_bot.application.retrieval.context_assembler import ContextAssembler
from l1_support_bot.domain.models.chunk import ChunkMetadata, KnowledgeChunk
from l1_support_bot.domain.ports.vector_store import VectorSearchResult


def result(document_name: str, text: str, sequence: int = 0) -> VectorSearchResult:
    chunk = KnowledgeChunk.new(
        document_id=uuid4(),
        ingestion_job_id=uuid4(),
        sequence=sequence,
        text=text,
        metadata=ChunkMetadata(document_name=document_name),
    )
    return VectorSearchResult(chunk, 0.9)


def test_context_keeps_material_sources_and_deduplicates_fusion_hits() -> None:
    first = result("task-codes.pdf", "BA435 opens the customer account screen.")
    second = result("operations-rca.pdf", "The account screen requires branch setup.")

    context = ContextAssembler().assemble((first, first, second), max_chunks=5)

    assert context.count("chunk_id=") == 2
    assert "document=task-codes.pdf" in context
    assert "document=operations-rca.pdf" in context
    assert context.count(first.chunk.text) == 1


def test_context_limit_does_not_duplicate_reference_numbers() -> None:
    results = tuple(result(f"manual-{index}.pdf", f"Source {index}.") for index in range(3))

    context = ContextAssembler().assemble(results, max_chunks=2)

    assert re.findall(r"\[REFERENCE (\d+) \|", context) == ["1", "2"]
    assert "manual-2.pdf" not in context