"""Default infrastructure wiring for local development."""

from sqlalchemy.ext.asyncio import AsyncEngine

from l1_support_bot.application.ingestion.cleanup_document import CleanupDocument
from l1_support_bot.application.ingestion.process_document import ProcessDocument
from l1_support_bot.application.ingestion.reindex_document import ReindexDocument
from l1_support_bot.domain.models.configuration import (
    ChunkingConfig,
    EmbeddingConfig,
    LLMConfig,
    RetrievalConfig,
)
from l1_support_bot.infrastructure.chunking.structure_aware_chunker import StructureAwareChunker
from l1_support_bot.infrastructure.configuration.runtime_config_cache import (
    InMemoryRuntimeConfigurationCache,
)
from l1_support_bot.infrastructure.embedding.http_embedding import HttpEmbeddingAdapter
from l1_support_bot.infrastructure.file_storage.local import LocalFileStorage
from l1_support_bot.infrastructure.jobs.sqlalchemy_job_queue import SqlAlchemyJobQueue
from l1_support_bot.infrastructure.llm.ollama_client import OllamaClient
from l1_support_bot.infrastructure.parsing.docling_parser import DoclingParser
from l1_support_bot.infrastructure.parsing.flexcube_metadata_extractor import (
    FlexcubeMetadataExtractor,
)
from l1_support_bot.infrastructure.parsing.parser_router import FallbackParserRouter
from l1_support_bot.infrastructure.parsing.pymupdf_parser import PyMuPDFParser
from l1_support_bot.infrastructure.parsing.python_docx_parser import PythonDocxParser
from l1_support_bot.infrastructure.persistence.database import create_engine_and_session_factory
from l1_support_bot.infrastructure.persistence.sqlalchemy.chunk_repository import (
    SqlAlchemyChunkRepository,
)
from l1_support_bot.infrastructure.persistence.sqlalchemy.document_repository import (
    SqlAlchemyDocumentRepository,
)
from l1_support_bot.infrastructure.persistence.sqlalchemy.feedback_repository import (
    SqlAlchemyFeedbackRepository,
)
from l1_support_bot.infrastructure.persistence.sqlalchemy.ingestion_job_repository import (
    SqlAlchemyIngestionJobRepository,
)
from l1_support_bot.infrastructure.persistence.sqlalchemy.configuration_repository import (
    SqlAlchemyConfigurationRepository,
)
from l1_support_bot.infrastructure.retrieval.hybrid_retriever import HybridRetriever
from l1_support_bot.infrastructure.session.in_memory_session_store import InMemorySessionStore
from l1_support_bot.infrastructure.vector_store.qdrant_index_manager import QdrantIndexManager
from l1_support_bot.infrastructure.vector_store.qdrant_store import QdrantVectorStore
from l1_support_bot.interface.config import Settings
from l1_support_bot.interface.dependencies import PortDependencies
from l1_support_bot.worker.runner import IngestionWorker


def build_default_dependencies(settings: Settings) -> tuple[AsyncEngine, PortDependencies]:
    engine, session_factory = create_engine_and_session_factory(settings.database_url)
    job_queue = SqlAlchemyJobQueue(session_factory)
    document_repository = SqlAlchemyDocumentRepository(session_factory)
    ingestion_job_repository = SqlAlchemyIngestionJobRepository(session_factory)
    chunk_repository = SqlAlchemyChunkRepository(session_factory)
    file_storage = LocalFileStorage(settings.file_storage_path)
    parser = FallbackParserRouter(
        DoclingParser(validated=False), PyMuPDFParser(), PythonDocxParser()
    )
    chunker = StructureAwareChunker()
    embedding_config = EmbeddingConfig(
        provider="openai_compatible",
        model=settings.embedding_model,
        model_version=settings.embedding_model_version,
        endpoint=settings.embedding_base_url,
        dimensions=settings.embedding_dimensions,
        batch_size=settings.embedding_batch_size,
        timeout_seconds=settings.embedding_timeout_seconds,
        index_compat_id=(
            f"openai_compatible:{settings.embedding_model}:"
            f"{settings.embedding_model_version}:{settings.embedding_dimensions}"
        ),
    )
    embedding = HttpEmbeddingAdapter()
    vector_store = QdrantVectorStore(
        url=settings.qdrant_url,
        dimensions=settings.embedding_dimensions,
    )
    index_manager = QdrantIndexManager(vector_store)
    cleanup = CleanupDocument(
        documents=document_repository,
        jobs=ingestion_job_repository,
        chunks=chunk_repository,
        diagnostics=chunk_repository,
        vectors=vector_store,
        storage=file_storage,
    )
    reindex = ReindexDocument(
        documents=document_repository,
        jobs=ingestion_job_repository,
        storage=file_storage,
        parser=parser,
        chunker=chunker,
        chunks=chunk_repository,
        embedding=embedding,
        embedding_config=embedding_config,
        index_manager=index_manager,
        metadata_extractor=FlexcubeMetadataExtractor(),
    )
    llm_config = LLMConfig(
        provider="ollama",
        model=settings.ollama_model,
        endpoint=settings.ollama_base_url,
        timeout_seconds=settings.ollama_timeout_seconds,
    )
    retrieval_config = RetrievalConfig()
    runtime_cache = InMemoryRuntimeConfigurationCache(
        llm=llm_config,
        embedding=embedding_config,
        retrieval=retrieval_config,
        chunking=ChunkingConfig(),
        repository=SqlAlchemyConfigurationRepository(session_factory),
    )
    return engine, PortDependencies(
        document_repository=document_repository,
        feedback_repository=SqlAlchemyFeedbackRepository(session_factory),
        ingestion_job_repository=ingestion_job_repository,
        cleanup_document=cleanup,
        file_storage=file_storage,
        parser=parser,
        chunker=chunker,
        chunk_repository=chunk_repository,
        configuration_repository=SqlAlchemyConfigurationRepository(session_factory),
        job_queue=job_queue,
        embedding=embedding,
        vector_store=vector_store,
        index_manager=index_manager,
        reindex_document=reindex,
        retriever=HybridRetriever(
            vector_store=vector_store,
            embedding=embedding,
            embedding_config=embedding_config,
        ),
        llm=OllamaClient(),
        session_store=InMemorySessionStore(
            max_messages=settings.session_history_window_turns * 2
        ),
        runtime_configuration_cache=runtime_cache,
    )


def build_default_worker(settings: Settings) -> tuple[AsyncEngine, IngestionWorker]:
    engine, dependencies = build_default_dependencies(settings)
    if (
        dependencies.document_repository is None
        or dependencies.ingestion_job_repository is None
        or dependencies.file_storage is None
        or dependencies.parser is None
        or dependencies.chunker is None
        or dependencies.chunk_repository is None
        or dependencies.job_queue is None
    ):
        raise RuntimeError("Default ingestion dependencies are incomplete")
    processor = ProcessDocument(
        document_repository=dependencies.document_repository,
        ingestion_job_repository=dependencies.ingestion_job_repository,
        file_storage=dependencies.file_storage,
        parser=dependencies.parser,
        chunker=dependencies.chunker,
        chunk_repository=dependencies.chunk_repository,
        metadata_extractor=FlexcubeMetadataExtractor(),
        embedding=dependencies.embedding,
        vector_store=dependencies.vector_store,
        embedding_config=EmbeddingConfig(
            provider="openai_compatible",
            model=settings.embedding_model,
            model_version=settings.embedding_model_version,
            endpoint=settings.embedding_base_url,
            dimensions=settings.embedding_dimensions,
            batch_size=settings.embedding_batch_size,
            timeout_seconds=settings.embedding_timeout_seconds,
            index_compat_id=(
                f"openai_compatible:{settings.embedding_model}:"
                f"{settings.embedding_model_version}:{settings.embedding_dimensions}"
            ),
        ),
    )
    return engine, IngestionWorker(
        queue=dependencies.job_queue,
        jobs=dependencies.ingestion_job_repository,
        documents=dependencies.document_repository,
        process=processor.execute,
    )
