"""Validate generated answers against the evidence retrieved for the question."""

from collections.abc import Collection, Sequence
from uuid import UUID

from l1_support_bot.domain.errors import CitationValidationError
from l1_support_bot.domain.models.answer import Answer, AnswerType
from l1_support_bot.domain.ports.vector_store import VectorSearchResult


class ResponseValidator:
    def validate(
        self,
        answer: Answer,
        *,
        retrieved: Sequence[VectorSearchResult],
        available_document_ids: Collection[UUID] | None = None,
    ) -> Answer:
        if answer.answer_type in {
            AnswerType.INSUFFICIENT,
            AnswerType.AMBIGUOUS,
            AnswerType.INCORRECT_PREMISE,
        }:
            if answer.citations:
                raise CitationValidationError(
                    f"{answer.answer_type.value} responses cannot contain citations."
                )
            return answer

        if answer.answer_type not in {AnswerType.GROUNDED, AnswerType.PARTIAL}:
            raise CitationValidationError("Answer has an unsupported answer type.")
        if not answer.citations:
            raise CitationValidationError("Supported answers require at least one citation.")

        retrieved_by_id = {result.chunk.id: result for result in retrieved}
        seen: set[UUID] = set()
        for citation in answer.citations:
            if citation.chunk_id in seen:
                raise CitationValidationError("A citation cannot reference the same chunk twice.")
            result = retrieved_by_id.get(citation.chunk_id)
            if result is None:
                raise CitationValidationError(
                    f"Citation chunk {citation.chunk_id} was not retrieved for this question."
                )
            if citation.document_id != result.chunk.document_id:
                raise CitationValidationError(
                    "Citation document does not match its retrieved chunk."
                )
            if (
                available_document_ids is not None
                and citation.document_id not in available_document_ids
            ):
                raise CitationValidationError(
                    f"Citation document {citation.document_id} is not available."
                )
            self._validate_source_metadata(citation, result)
            seen.add(citation.chunk_id)
        return answer

    @staticmethod
    def _validate_source_metadata(citation: object, result: VectorSearchResult) -> None:
        metadata = result.chunk.metadata
        expected = {
            "document_name": metadata.document_name,
            "page_number": metadata.page_number,
            "section": metadata.section,
            "task_code": metadata.task_code,
            "screen_name": metadata.screen_name,
            "menu_path": metadata.menu_path,
            "prerequisites": metadata.prerequisites,
            "modes": metadata.modes,
            "field_names": metadata.field_names,
            "procedure_steps": metadata.procedure_steps,
            "error_code": metadata.error_code,
            "jira_id": metadata.jira_id,
            "rca_reference": metadata.rca_reference,
            "source_type": metadata.source_type,
        }
        for name, value in expected.items():
            if getattr(citation, name) != value:
                raise CitationValidationError(
                    f"Citation metadata {name} does not match the retrieved source."
                )
