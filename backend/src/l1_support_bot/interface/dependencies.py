"""Composition-root dependency wiring for domain-owned ports."""

from dataclasses import dataclass
from typing import TypeVar, cast

from fastapi import FastAPI, Request

from l1_support_bot.domain.ports import (
    ChunkerPort,
    ChunkRepository,
    ConfigurationRepository,
    DocumentRepository,
    EmbeddingPort,
    FeedbackRepository,
    FileStoragePort,
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
    chunk_repository: ChunkRepository | None = None
    feedback_repository: FeedbackRepository | None = None
    configuration_repository: ConfigurationRepository | None = None
    file_storage: FileStoragePort | None = None
    parser: ParserPort | None = None
    chunker: ChunkerPort | None = None
    embedding: EmbeddingPort | None = None
    vector_store: VectorStorePort | None = None
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