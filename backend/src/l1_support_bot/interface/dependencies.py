"""Composition-root dependency wiring for domain-owned ports."""

from dataclasses import dataclass
from typing import TypeVar, cast

from fastapi import FastAPI, Request

from l1_support_bot.application.ingestion.cleanup_document import CleanupDocument
from l1_support_bot.application.ingestion.reindex_document import ReindexDocument
from l1_support_bot.domain.errors import DatabaseUnavailableError
from l1_support_bot.domain.ports import (
    ChunkerPort,
    ChunkRepository,
    ConfigurationRepository,
    DocumentRepository,
    EmbeddingPort,
    FeedbackRepository,
    FileStoragePort,
    IndexManagerPort,
    IngestionJobRepository,
    JobQueuePort,
    LLMPort,
    ParserPort,
    RerankerPort,
    RetrieverPort,
    RuntimeConfigurationCache,
    SessionStore,
    VectorStorePort,
)


@dataclass(slots=True)
class PortDependencies:
    document_repository: DocumentRepository | None = None
    ingestion_job_repository: IngestionJobRepository | None = None
    cleanup_document: CleanupDocument | None = None
    chunk_repository: ChunkRepository | None = None
    feedback_repository: FeedbackRepository | None = None
    configuration_repository: ConfigurationRepository | None = None
    file_storage: FileStoragePort | None = None
    parser: ParserPort | None = None
    chunker: ChunkerPort | None = None
    embedding: EmbeddingPort | None = None
    vector_store: VectorStorePort | None = None
    index_manager: IndexManagerPort | None = None
    reindex_document: ReindexDocument | None = None
    retriever: RetrieverPort | None = None
    reranker: RerankerPort | None = None
    llm: LLMPort | None = None
    job_queue: JobQueuePort | None = None
    session_store: SessionStore | None = None
    runtime_configuration_cache: RuntimeConfigurationCache | None = None


PortT = TypeVar("PortT")


def install_dependencies(app: FastAPI, dependencies: PortDependencies) -> None:
    app.state.dependencies = dependencies


def get_dependencies(request: Request) -> PortDependencies:
    return cast(PortDependencies, request.app.state.dependencies)


def get_port(request: Request, name: str) -> PortT | None:
    return getattr(get_dependencies(request), name, None)


async def ensure_persistence_available(request: Request) -> None:
    """Fail closed for mutations when authoritative relational persistence is down."""

    dependencies = get_dependencies(request)
    cache = dependencies.runtime_configuration_cache
    if cache is None:
        return
    try:
        await cache.refresh()
    except Exception as exc:
        raise DatabaseUnavailableError() from exc
    if not cache.persistence_available:
        raise DatabaseUnavailableError()