"""Application-owned infrastructure ports."""

from l1_support_bot.domain.ports.chunking import ChunkerPort
from l1_support_bot.domain.ports.embedding import EmbeddingPort
from l1_support_bot.domain.ports.feedback_repository import FeedbackRepository
from l1_support_bot.domain.ports.file_storage import FileStoragePort, StoredFile
from l1_support_bot.domain.ports.index_manager import IndexGeneration, IndexManagerPort
from l1_support_bot.domain.ports.job_queue import JobQueuePort
from l1_support_bot.domain.ports.llm import LLMPort
from l1_support_bot.domain.ports.metadata import MetadataExtractorPort
from l1_support_bot.domain.ports.parsing import DocumentParserPort, ParserPort
from l1_support_bot.domain.ports.repositories import (
    ChunkRepository,
    ConfigurationRepository,
    DiagnosticRepository,
    DocumentRepository,
    IngestionJobRepository,
)
from l1_support_bot.domain.ports.reranker import RerankerPort
from l1_support_bot.domain.ports.retrieval import RetrieverPort
from l1_support_bot.domain.ports.runtime_configuration import RuntimeConfigurationCache
from l1_support_bot.domain.ports.session_store import SessionStore
from l1_support_bot.domain.ports.vector_store import (
    VectorSearchResult,
    VectorStore,
    VectorStorePort,
)

__all__ = [
    "ChunkerPort",
    "ChunkRepository",
    "ConfigurationRepository",
    "DiagnosticRepository",
    "DocumentParserPort",
    "DocumentRepository",
    "EmbeddingPort",
    "FeedbackRepository",
    "FileStoragePort",
    "IndexGeneration",
    "IndexManagerPort",
    "IngestionJobRepository",
    "JobQueuePort",
    "LLMPort",
    "MetadataExtractorPort",
    "ParserPort",
    "RerankerPort",
    "RetrieverPort",
    "RuntimeConfigurationCache",
    "SessionStore",
    "StoredFile",
    "VectorSearchResult",
    "VectorStore",
    "VectorStorePort",
]
