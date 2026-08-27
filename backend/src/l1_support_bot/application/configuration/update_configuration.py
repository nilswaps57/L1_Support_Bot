"""Validate, persist, and publish one complete configuration snapshot."""

from dataclasses import dataclass

from l1_support_bot.application.configuration.validate_configuration import (
    validate_configuration,
)
from l1_support_bot.application.configuration.validate_embedding import ValidateEmbedding
from l1_support_bot.application.configuration.validate_index_compatibility import (
    check_index_compatibility,
)
from l1_support_bot.application.configuration.validate_llm import ValidateLLM
from l1_support_bot.domain.errors import ReindexRequiredError
from l1_support_bot.domain.models.configuration import (
    ChunkingConfig,
    ConfigurationSnapshot,
    EmbeddingConfig,
    LLMConfig,
    RetrievalConfig,
)
from l1_support_bot.domain.ports.repositories import ConfigurationRepository
from l1_support_bot.domain.ports.runtime_configuration import RuntimeConfigurationCache


@dataclass(frozen=True, slots=True)
class ActivationResult:
    configuration: ConfigurationSnapshot
    status: str = "active"
    requires_reindex: bool = False
    reindex_reasons: tuple[str, ...] = ()


class UpdateConfiguration:
    def __init__(
        self,
        *,
        repository: ConfigurationRepository,
        cache: RuntimeConfigurationCache,
        llm_validator: ValidateLLM | None = None,
        embedding_validator: ValidateEmbedding | None = None,
    ) -> None:
        self.repository = repository
        self.cache = cache
        self.llm_validator = llm_validator
        self.embedding_validator = embedding_validator

    async def execute(
        self,
        *,
        llm: LLMConfig,
        embedding: EmbeddingConfig,
        retrieval: RetrievalConfig,
        chunking: ChunkingConfig,
        confirm_reindex: bool = False,
    ) -> ActivationResult:
        current_embedding = await self.repository.get_embedding()
        current_chunking = await self.repository.get_chunking()
        indexed_documents = await self.repository.count_indexed_documents()
        compatibility = check_index_compatibility(
            current_embedding=current_embedding or embedding,
            proposed_embedding=embedding,
            current_chunking=current_chunking or chunking,
            proposed_chunking=chunking,
            indexed_documents=indexed_documents,
        )
        if compatibility.requires_reindex and indexed_documents:
            raise ReindexRequiredError(
                "Embedding or chunking changes require a successful re-index before activation.",
                details={
                    "indexed_documents": str(indexed_documents),
                    "confirmation_required": "true",
                },
            )
        validate_configuration(llm=llm, embedding=embedding, retrieval=retrieval, chunking=chunking)
        if self.llm_validator is not None:
            await self.llm_validator.execute(llm)
        if self.embedding_validator is not None:
            await self.embedding_validator.execute(embedding)
        snapshot = ConfigurationSnapshot(
            llm=llm, embedding=embedding, retrieval=retrieval, chunking=chunking
        )
        await self.repository.save_all(snapshot)
        await self.cache.refresh()
        return ActivationResult(configuration=snapshot)
