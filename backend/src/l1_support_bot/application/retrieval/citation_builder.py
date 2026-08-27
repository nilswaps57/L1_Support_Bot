"""Construct citations from explicit references in a generated answer."""

from collections.abc import Collection, Sequence
from uuid import UUID

from l1_support_bot.domain.errors import CitationValidationError
from l1_support_bot.domain.models.citation import Citation
from l1_support_bot.domain.ports.vector_store import VectorSearchResult


class CitationBuilder:
    def build(
        self,
        retrieved: Sequence[VectorSearchResult],
        *,
        supported_chunk_ids: Sequence[UUID | str],
        available_document_ids: Collection[UUID] | None = None,
    ) -> tuple[Citation, ...]:
        if not supported_chunk_ids:
            raise CitationValidationError(
                "A grounded answer must identify at least one supported chunk."
            )

        retrieved_by_id = {result.chunk.id: result for result in retrieved}
        citations: list[Citation] = []
        seen: set[UUID] = set()
        for raw_chunk_id in supported_chunk_ids:
            chunk_id = self._chunk_id(raw_chunk_id)
            if chunk_id in seen:
                raise CitationValidationError("A citation cannot reference the same chunk twice.")
            result = retrieved_by_id.get(chunk_id)
            if result is None:
                raise CitationValidationError(
                    f"Citation chunk {chunk_id} was not retrieved for this question."
                )
            if (
                available_document_ids is not None
                and result.chunk.document_id not in available_document_ids
            ):
                raise CitationValidationError(
                    f"Citation document {result.chunk.document_id} is not available."
                )
            citations.append(self._from_result(result))
            seen.add(chunk_id)
        return tuple(citations)

    @staticmethod
    def _chunk_id(value: UUID | str) -> UUID:
        try:
            return value if isinstance(value, UUID) else UUID(value)
        except (AttributeError, ValueError) as exc:
            raise CitationValidationError("Citation contains an invalid chunk identity.") from exc

    @staticmethod
    def _from_result(result: VectorSearchResult) -> Citation:
        metadata = result.chunk.metadata
        return Citation(
            chunk_id=result.chunk.id,
            document_id=result.chunk.document_id,
            document_name=metadata.document_name,
            page_number=metadata.page_number,
            section=metadata.section,
            task_code=metadata.task_code,
            screen_name=metadata.screen_name,
            menu_path=metadata.menu_path,
            prerequisites=metadata.prerequisites,
            modes=metadata.modes,
            field_names=metadata.field_names,
            procedure_steps=metadata.procedure_steps,
            error_code=metadata.error_code,
            jira_id=metadata.jira_id,
            rca_reference=metadata.rca_reference,
            source_type=metadata.source_type,
            relevance_score=result.score,
        )
