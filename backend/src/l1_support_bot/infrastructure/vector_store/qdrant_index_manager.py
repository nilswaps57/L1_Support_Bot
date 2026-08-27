"""Qdrant-backed isolated generations with lock-protected cutover."""

from uuid import UUID

from l1_support_bot.domain.models.chunk import KnowledgeChunk
from l1_support_bot.domain.ports.index_manager import IndexGeneration, IndexManagerPort
from l1_support_bot.infrastructure.vector_store.qdrant_store import QdrantVectorStore


class QdrantIndexManager(IndexManagerPort):
    def __init__(self, store: QdrantVectorStore) -> None:
        self.store = store
        self._collections: dict[str, str] = {}

    async def begin_staging(
        self,
        document_id: UUID,
        *,
        embedding_model_id: str,
        chunking_config_id: str | None,
    ) -> IndexGeneration:
        collection = await self.store.create_staging_collection()
        await self.store.clone_active_without_document(collection, document_id)
        generation = IndexGeneration(collection, embedding_model_id, chunking_config_id)
        self._collections[generation.generation_id] = collection
        return generation

    async def stage(
        self,
        generation: IndexGeneration,
        chunks: tuple[KnowledgeChunk, ...],
        vectors: tuple[tuple[float, ...], ...],
    ) -> None:
        await self.store.upsert_to_collection(generation.generation_id, chunks, vectors)

    async def validate(
        self,
        generation: IndexGeneration,
        *,
        document_id: UUID,
        expected_chunks: int,
        embedding_model_id: str,
    ) -> None:
        await self.store.validate_collection(
            generation.generation_id,
            document_id=document_id,
            expected_chunks=expected_chunks,
            embedding_model_id=embedding_model_id,
        )

    async def cutover(self, generation: IndexGeneration) -> IndexGeneration | None:
        previous_collection = await self.store.activate_collection(generation.generation_id)
        return IndexGeneration(previous_collection, "", None)

    async def rollback(self, generation: IndexGeneration) -> None:
        await self.store.activate_collection(generation.generation_id)

    async def cleanup(self, generation: IndexGeneration) -> None:
        await self.store.delete_collection(generation.generation_id)
        self._collections.pop(generation.generation_id, None)
