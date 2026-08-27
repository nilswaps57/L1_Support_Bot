from dataclasses import replace

import pytest

from l1_support_bot.application.configuration.validate_configuration import (
    validate_configuration,
)
from l1_support_bot.application.configuration.validate_index_compatibility import (
    check_index_compatibility,
)
from l1_support_bot.domain.models.configuration import (
    ChunkingConfig,
    EmbeddingConfig,
    LLMConfig,
    RetrievalConfig,
)


def test_valid_configuration_categories_are_accepted() -> None:
    configuration = validate_configuration(
        llm=LLMConfig(provider="ollama", model="phi3.5", endpoint="http://localhost"),
        embedding=EmbeddingConfig(
            provider="ollama",
            model="nomic-embed-text",
            model_version="1",
            endpoint="http://localhost",
            dimensions=768,
            index_compat_id="ollama:nomic-embed-text:1:768",
        ),
        retrieval=RetrievalConfig(),
        chunking=ChunkingConfig(),
    )

    assert configuration.llm.model == "phi3.5"
    assert configuration.embedding.dimensions == 768


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("model", ""),
        ("endpoint", "file:///tmp/provider"),
        ("temperature", -0.1),
        ("temperature", 2.1),
        ("max_tokens", 0),
        ("context_window", 0),
        ("timeout_seconds", 0),
        ("max_retries", -1),
    ],
)
def test_invalid_llm_values_are_rejected(field: str, value: object) -> None:
    with pytest.raises(ValueError):
        LLMConfig(
            provider=value if field == "provider" else "ollama",
            model=value if field == "model" else "phi3.5",
            endpoint=value if field == "endpoint" else "http://localhost",
            temperature=value if field == "temperature" else 0.1,
            max_tokens=value if field == "max_tokens" else 2048,
            context_window=value if field == "context_window" else 4096,
            timeout_seconds=value if field == "timeout_seconds" else 30,
            max_retries=value if field == "max_retries" else 2,
        )


@pytest.mark.parametrize(
    "changes",
    [
        {"dimensions": 0},
        {"batch_size": 0},
        {"timeout_seconds": 0},
        {"distance_method": "manhattan"},
        {"index_compat_id": ""},
    ],
)
def test_invalid_embedding_values_are_rejected(changes: dict[str, object]) -> None:
    with pytest.raises(ValueError):
        EmbeddingConfig(
            provider=changes.get("provider", "ollama"),
            model="nomic-embed-text",
            model_version="1",
            endpoint="http://localhost",
            dimensions=changes.get("dimensions", 768),
            index_compat_id=changes.get("index_compat_id", "ollama:nomic:1:768"),
            distance_method=changes.get("distance_method", "cosine"),
            batch_size=changes.get("batch_size", 32),
            timeout_seconds=changes.get("timeout_seconds", 30),
        )


@pytest.mark.parametrize(
    "changes",
    [
        {"top_k_candidates": 0},
        {"final_top_k": 0},
        {"final_top_k": 21},
        {"similarity_threshold": -0.1},
        {"similarity_threshold": 1.1},
        {"dense_weight": -0.1},
        {"dense_weight": 0.8, "sparse_weight": 0.3},
        {"rerank_top_k": 0},
        {"min_evidence_tokens": 0},
    ],
)
def test_invalid_retrieval_values_are_rejected(changes: dict[str, object]) -> None:
    with pytest.raises(ValueError):
        RetrievalConfig(**changes)


@pytest.mark.parametrize(
    "changes",
    [
        {"strategy": "UNKNOWN"},
        {"min_chunk_tokens": 0},
        {"min_chunk_tokens": 513, "target_chunk_tokens": 512},
        {"target_chunk_tokens": 1025, "max_chunk_tokens": 1024},
        {"overlap_tokens": -1},
        {"overlap_tokens": 1024},
    ],
)
def test_invalid_chunking_values_are_rejected(changes: dict[str, object]) -> None:
    with pytest.raises(ValueError):
        ChunkingConfig(**changes)


def test_embedding_or_chunking_identity_requires_reindex() -> None:
    current_embedding = EmbeddingConfig(
        provider="ollama",
        model="nomic-embed-text",
        model_version="1",
        endpoint="http://localhost",
        dimensions=768,
        index_compat_id="ollama:nomic-embed-text:1:768",
    )
    current_chunking = ChunkingConfig()
    proposed_embedding = replace(current_embedding, model="bge-m3", index_compat_id="bge-m3:1:1024")
    proposed_dimensions = replace(current_embedding, dimensions=1024)
    proposed_chunking = replace(current_chunking, target_chunk_tokens=640)

    embedding_result = check_index_compatibility(
        current_embedding=current_embedding,
        proposed_embedding=proposed_embedding,
        current_chunking=current_chunking,
        proposed_chunking=current_chunking,
        indexed_documents=3,
    )
    chunking_result = check_index_compatibility(
        current_embedding=current_embedding,
        proposed_embedding=current_embedding,
        current_chunking=current_chunking,
        proposed_chunking=proposed_chunking,
        indexed_documents=3,
    )
    dimensions_result = check_index_compatibility(
        current_embedding=current_embedding,
        proposed_embedding=proposed_dimensions,
        current_chunking=current_chunking,
        proposed_chunking=current_chunking,
        indexed_documents=3,
    )

    assert embedding_result.requires_reindex
    assert chunking_result.requires_reindex
    assert dimensions_result.requires_reindex
    assert embedding_result.indexed_documents == 3


def test_unchanged_compatible_configuration_does_not_require_reindex() -> None:
    embedding = EmbeddingConfig(
        provider="ollama",
        model="nomic-embed-text",
        model_version="1",
        endpoint="http://localhost",
        dimensions=768,
        index_compat_id="ollama:nomic-embed-text:1:768",
    )

    result = check_index_compatibility(
        current_embedding=embedding,
        proposed_embedding=embedding,
        current_chunking=ChunkingConfig(),
        proposed_chunking=ChunkingConfig(),
        indexed_documents=0,
    )

    assert not result.requires_reindex
    assert result.reasons == ()
