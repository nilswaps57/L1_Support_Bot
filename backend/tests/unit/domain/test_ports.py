from l1_support_bot.domain.ports import (
    ChunkerPort,
    DocumentRepository,
    EmbeddingPort,
    FileStoragePort,
    JobQueuePort,
    LLMPort,
    ParserPort,
    RerankerPort,
    RetrieverPort,
    RuntimeConfigurationCache,
    SessionStore,
    VectorStorePort,
)


def test_ports_are_runtime_checkable_protocols() -> None:
    ports = (
        DocumentRepository,
        FileStoragePort,
        ParserPort,
        ChunkerPort,
        EmbeddingPort,
        VectorStorePort,
        RetrieverPort,
        RerankerPort,
        LLMPort,
        JobQueuePort,
        SessionStore,
        RuntimeConfigurationCache,
    )

    assert all(getattr(port, "_is_protocol", False) for port in ports)