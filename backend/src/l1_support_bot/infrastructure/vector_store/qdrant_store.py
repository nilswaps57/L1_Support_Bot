"""Qdrant vector-store adapter using the standalone HTTP/local client."""

from __future__ import annotations

import asyncio
from collections.abc import Mapping, Sequence
from importlib import import_module
from typing import Any
from uuid import UUID, uuid4

from l1_support_bot.domain.errors import VectorStoreUnavailableError
from l1_support_bot.domain.models.chunk import ChunkMetadata, KnowledgeChunk
from l1_support_bot.domain.ports.vector_store import VectorSearchResult, VectorStorePort


class QdrantVectorStore(VectorStorePort):
    def __init__(
        self,
        *,
        client: Any | None = None,
        url: str = "http://localhost:6333",
        collection_name: str = "l1_support_bot_chunks",
        dimensions: int = 768,
    ) -> None:
        self.client = client or import_module("qdrant_client").QdrantClient(url=url)
        self.collection_name = collection_name
        self.dimensions = dimensions
        self._active_collection_name = collection_name
        self._known_collections = {collection_name}
        self._generation_lock = asyncio.Lock()

    async def upsert(
        self, chunks: Sequence[KnowledgeChunk], vectors: Sequence[Sequence[float]]
    ) -> None:
        if len(chunks) != len(vectors):
            raise ValueError("Qdrant upsert requires one vector per chunk")
        await self._ensure_collection(self._active_collection())
        await self._upsert_collection(self._active_collection(), chunks, vectors)

    async def create_staging_collection(self) -> str:
        name = f"{self.collection_name}__staging__{uuid4().hex}"
        self._known_collections.add(name)
        await self._ensure_collection(name)
        return name

    async def clone_active_without_document(self, collection_name: str, document_id: UUID) -> None:
        active = self._active_collection()
        if active == collection_name:
            raise ValueError("A staging collection must differ from the active collection")
        try:
            records, _ = await asyncio.to_thread(
                self.client.scroll,
                collection_name=active,
                limit=10000,
                with_payload=True,
                with_vectors=True,
            )
            qdrant = import_module("qdrant_client.models")
            points = []
            for record in records:
                if record.payload.get("document_id") == str(document_id):
                    continue
                vector = record.vector
                if isinstance(vector, dict):
                    vector = next(iter(vector.values()))
                if vector is not None:
                    points.append(
                        qdrant.PointStruct(
                            id=record.id, vector=list(vector), payload=record.payload
                        )
                    )
            if points:
                await asyncio.to_thread(
                    self.client.upsert,
                    collection_name=collection_name,
                    points=points,
                    wait=True,
                )
        except Exception as exc:
            raise VectorStoreUnavailableError(
                "The replacement index could not be prepared."
            ) from exc

    async def upsert_to_collection(
        self,
        collection_name: str,
        chunks: Sequence[KnowledgeChunk],
        vectors: Sequence[Sequence[float]],
    ) -> None:
        await self._ensure_collection(collection_name)
        await self._upsert_collection(collection_name, chunks, vectors)

    async def validate_collection(
        self,
        collection_name: str,
        *,
        document_id: UUID,
        expected_chunks: int,
        embedding_model_id: str,
    ) -> None:
        records, _ = await asyncio.to_thread(
            self.client.scroll,
            collection_name=collection_name,
            scroll_filter=self._filter({"document_id": str(document_id)}),
            limit=10000,
            with_payload=True,
        )
        if len(records) != expected_chunks or any(
            record.payload.get("embedding_model_id") != embedding_model_id for record in records
        ):
            raise VectorStoreUnavailableError("The replacement index failed validation.")

    async def activate_collection(self, collection_name: str) -> str:
        await self._ensure_collection(collection_name)
        async with self._generation_lock:
            previous = self._active_collection_name
            self._active_collection_name = collection_name
            return previous

    async def delete_collection(self, collection_name: str) -> None:
        async with self._generation_lock:
            if collection_name == self._active_collection_name:
                raise ValueError("The active index cannot be deleted")
        exists = await asyncio.to_thread(self.client.collection_exists, collection_name)
        if exists:
            await asyncio.to_thread(self.client.delete_collection, collection_name)
        self._known_collections.discard(collection_name)

    def _active_collection(self) -> str:
        return self._active_collection_name

    async def _upsert_collection(
        self,
        collection_name: str,
        chunks: Sequence[KnowledgeChunk],
        vectors: Sequence[Sequence[float]],
    ) -> None:
        try:
            qdrant = import_module("qdrant_client.models")
            points = [
                qdrant.PointStruct(
                    id=str(chunk.id), vector=list(vector), payload=self._payload(chunk)
                )
                for chunk, vector in zip(chunks, vectors, strict=True)
            ]
            await asyncio.to_thread(
                self.client.upsert,
                collection_name=collection_name,
                points=points,
                wait=True,
            )
        except Exception as exc:
            raise VectorStoreUnavailableError(
                "Vector indexing is temporarily unavailable."
            ) from exc

    async def search_dense(
        self,
        vector: Sequence[float],
        *,
        limit: int,
        filters: Mapping[str, str] | None = None,
    ) -> Sequence[VectorSearchResult]:
        collection_name = self._active_collection()
        await self._ensure_collection(collection_name)
        try:
            query_filter = self._filter(filters)
            if hasattr(self.client, "query_points"):
                response = await asyncio.to_thread(
                    self.client.query_points,
                    collection_name=collection_name,
                    query=list(vector),
                    query_filter=query_filter,
                    limit=limit,
                    with_payload=True,
                )
                points = response.points
            else:
                points = await asyncio.to_thread(
                    self.client.search,
                    collection_name=collection_name,
                    query_vector=list(vector),
                    query_filter=query_filter,
                    limit=limit,
                    with_payload=True,
                )
            return tuple(self._result(point) for point in points)
        except Exception as exc:
            raise VectorStoreUnavailableError(
                "Vector search is temporarily unavailable."
            ) from exc

    async def search_sparse(
        self,
        terms: Sequence[str],
        *,
        limit: int,
        filters: Mapping[str, str] | None = None,
    ) -> Sequence[VectorSearchResult]:
        collection_name = self._active_collection()
        await self._ensure_collection(collection_name)
        try:
            records, _ = await asyncio.to_thread(
                self.client.scroll,
                collection_name=collection_name,
                scroll_filter=self._filter(filters),
                limit=10000,
                with_payload=True,
            )
            wanted = {term.lower().strip("?.!,") for term in terms}
            results = []
            for record in records:
                result = self._result(record)
                tokens = set(result.chunk.text.lower().split())
                score = len(wanted.intersection(tokens)) / max(len(wanted), 1)
                if score:
                    results.append(VectorSearchResult(result.chunk, score))
            return tuple(sorted(results, key=lambda item: item.score, reverse=True)[:limit])
        except Exception as exc:
            raise VectorStoreUnavailableError(
                "Lexical search is temporarily unavailable."
            ) from exc

    async def delete_by_document(self, document_id: UUID) -> None:
        collections = set(self._known_collections)
        if hasattr(self.client, "get_collections"):
            response = await asyncio.to_thread(self.client.get_collections)
            collections.update(collection.name for collection in response.collections)
        qdrant = import_module("qdrant_client.models")
        for collection_name in collections:
            await self._ensure_collection(collection_name)
            await asyncio.to_thread(
                self.client.delete,
                collection_name=collection_name,
                points_selector=qdrant.FilterSelector(
                    filter=qdrant.Filter(must=[qdrant.FieldCondition(
                        key="document_id", match=qdrant.MatchValue(value=str(document_id))
                    )])
                ),
                wait=True,
            )

    async def is_compatible(self, embedding_model_id: str) -> bool:
        await self._ensure_collection(self._active_collection())
        collection_name = self._active_collection()
        records, _ = await asyncio.to_thread(
            self.client.scroll,
            collection_name=collection_name,
            limit=10000,
            with_payload=True,
        )
        if not records:
            return True
        return all(
            record.payload.get("embedding_model_id") == embedding_model_id
            for record in records
        )

    async def _ensure_collection(self, collection_name: str) -> None:
        qdrant = import_module("qdrant_client.models")
        exists = await asyncio.to_thread(self.client.collection_exists, collection_name)
        if not exists:
            await asyncio.to_thread(
                self.client.create_collection,
                collection_name=collection_name,
                vectors_config=qdrant.VectorParams(
                    size=self.dimensions, distance=qdrant.Distance.COSINE
                ),
            )

    @staticmethod
    def _payload(chunk: KnowledgeChunk) -> dict[str, Any]:
        metadata = chunk.metadata
        return {
            "chunk_id": str(chunk.id), "document_id": str(chunk.document_id),
            "ingestion_job_id": str(chunk.ingestion_job_id),
            "chunk_seq": chunk.sequence,
            "document_name": metadata.document_name,
            "text": chunk.text, "embedding_model_id": chunk.embedding_model_id or "",
            "index_generation_id": chunk.index_generation_id or "",
            "source_type": metadata.source_type, "page_number": metadata.page_number,
            "section": metadata.section,
            "task_code": metadata.task_code, "screen_name": metadata.screen_name,
            "error_code": metadata.error_code, "jira_id": metadata.jira_id,
            "element_type": metadata.element_type,
        }

    @staticmethod
    def _filter(filters: Mapping[str, str] | None) -> Any:
        if not filters:
            return None
        qdrant = import_module("qdrant_client.models")
        return qdrant.Filter(must=[
            qdrant.FieldCondition(key=key, match=qdrant.MatchValue(value=value))
            for key, value in filters.items()
        ])

    @staticmethod
    def _result(point: Any) -> VectorSearchResult:
        payload = point.payload
        metadata = ChunkMetadata(
            document_name=payload["document_name"], page_number=payload.get("page_number"),
            source_type=payload.get("source_type"),
            section=payload.get("section"), task_code=payload.get("task_code"),
            screen_name=payload.get("screen_name"), error_code=payload.get("error_code"),
            jira_id=payload.get("jira_id"), element_type=payload.get("element_type", "paragraph"),
        )
        chunk = KnowledgeChunk(
            id=UUID(payload["chunk_id"]), document_id=UUID(payload["document_id"]),
            ingestion_job_id=UUID(payload["ingestion_job_id"]),
            sequence=int(payload.get("chunk_seq", 0)),
            text=payload["text"], metadata=metadata,
            embedding_model_id=payload.get("embedding_model_id"),
            index_generation_id=payload.get("index_generation_id"),
        )
        return VectorSearchResult(chunk, float(getattr(point, "score", 0.0)))
