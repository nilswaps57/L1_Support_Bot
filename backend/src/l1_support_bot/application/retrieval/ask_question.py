"""Generate a grounded answer from retrieved evidence only."""

from __future__ import annotations

import json
from collections.abc import Collection, Sequence
from dataclasses import replace
from typing import Protocol
from uuid import UUID

from l1_support_bot.application.retrieval.answer_outcomes import (
    ambiguous_answer,
    incorrect_premise_answer,
    insufficient_info_response,
    partial_answer,
)
from l1_support_bot.application.retrieval.citation_builder import CitationBuilder
from l1_support_bot.application.retrieval.evidence_sufficiency import (
    EvidenceStatus,
    EvidenceSufficiencyPolicy,
)
from l1_support_bot.application.retrieval.prompt_builder import PromptBuilder
from l1_support_bot.application.retrieval.response_validator import ResponseValidator
from l1_support_bot.application.security.query_sanitizer import QuerySanitizer
from l1_support_bot.application.security.response_disclosure_validator import (
    ResponseDisclosureValidator,
)
from l1_support_bot.application.shared.failure_mapping import map_infrastructure_error
from l1_support_bot.domain.errors import DatabaseUnavailableError, DomainError
from l1_support_bot.domain.models.answer import Answer, AnswerType
from l1_support_bot.domain.models.configuration import LLMConfig, RetrievalConfig
from l1_support_bot.domain.models.document import Document
from l1_support_bot.domain.models.session import ChatMessage
from l1_support_bot.domain.ports.llm import LLMPort
from l1_support_bot.domain.ports.repositories import DocumentRepository
from l1_support_bot.domain.ports.retrieval import RerankerPort, RetrieverPort
from l1_support_bot.domain.ports.vector_store import VectorSearchResult


class SecurityEventLogger(Protocol):
    def __call__(self, *, category: str, outcome: str) -> None: ...


class AskQuestion:
    def __init__(
        self,
        *,
        retriever: RetrieverPort,
        llm: LLMPort,
        llm_config: LLMConfig,
        retrieval_config: RetrievalConfig | None = None,
        prompt_builder: PromptBuilder | None = None,
        document_repository: DocumentRepository | None = None,
        citation_builder: CitationBuilder | None = None,
        response_validator: ResponseValidator | None = None,
        evidence_policy: EvidenceSufficiencyPolicy | None = None,
        reranker: RerankerPort | None = None,
        query_sanitizer: QuerySanitizer | None = None,
        disclosure_validator: ResponseDisclosureValidator | None = None,
        security_event_logger: SecurityEventLogger | None = None,
    ) -> None:
        self.retriever = retriever
        self.llm = llm
        self.llm_config = llm_config
        self.retrieval_config = retrieval_config or RetrievalConfig()
        self.prompt_builder = prompt_builder or PromptBuilder()
        self.document_repository = document_repository
        self.citation_builder = citation_builder or CitationBuilder()
        self.response_validator = response_validator or ResponseValidator()
        self.evidence_policy = evidence_policy or EvidenceSufficiencyPolicy(self.retrieval_config)
        self.reranker = reranker
        self.query_sanitizer = query_sanitizer or QuerySanitizer()
        self.disclosure_validator = disclosure_validator or ResponseDisclosureValidator()
        self.security_event_logger = security_event_logger

    async def execute(
        self,
        question: str,
        *,
        retrieval_question: str | None = None,
        conversation_context: Sequence[ChatMessage] = (),
    ) -> Answer:
        query_assessment = self.query_sanitizer.assess(question)
        if query_assessment.contains_injection and self.security_event_logger is not None:
            self.security_event_logger(
                category=",".join(query_assessment.categories),
                outcome="refused" if query_assessment.should_refuse else "grounding_required",
            )
        if query_assessment.should_refuse:
            return self._with_configuration_context(
                insufficient_info_response(
                    question,
                    "I can help with documented FLEXCUBE support questions, but I cannot "
                    "provide internal instructions, configuration, or execute commands.",
                )
            )
        normalized_retrieval_question = self.query_sanitizer.normalize_for_retrieval(
            retrieval_question or question
        )
        try:
            results = await self.retriever.retrieve(
                normalized_retrieval_question,
                limit=self.retrieval_config.top_k_candidates,
                config=self.retrieval_config,
            )
        except DomainError:
            raise
        except Exception as exc:
            raise map_infrastructure_error(exc, service="vector_store") from exc
        available_document_ids = await self._available_document_ids(tuple(results))
        if available_document_ids is not None:
            results = tuple(
                result for result in results if result.chunk.document_id in available_document_ids
            )
        assessment = self.evidence_policy.evaluate(question, tuple(results))
        if assessment.status is EvidenceStatus.INSUFFICIENT:
            return self._with_configuration_context(insufficient_info_response(question))
        if assessment.status is EvidenceStatus.INCORRECT_PREMISE:
            return self._with_configuration_context(incorrect_premise_answer(question))
        evidence = assessment.results
        if self.retrieval_config.rerank_enabled and self.reranker is not None:
            evidence = tuple(
                await self.reranker.rerank(
                    question,
                    evidence,
                    limit=self.retrieval_config.rerank_top_k,
                )
            )
        prompt = self.prompt_builder.build(
            question,
            tuple(evidence[: self.retrieval_config.final_top_k]),
            conversation_context=tuple(conversation_context),
        )
        try:
            raw = await self.llm.complete(prompt, config=self.llm_config)
        except DomainError:
            raise
        except Exception as exc:
            raise map_infrastructure_error(exc, service="llm") from exc
        payload = self._payload(raw)
        answer_type = self._answer_type(payload.get("answer_type"))
        answer_text = str(
            payload.get("answer_text")
            or (
                "The available knowledge sources do not contain sufficient information "
                "to answer this question."
            )
        )
        safe_answer_text = self.disclosure_validator.validate(answer_text)
        if safe_answer_text != answer_text:
            if self.security_event_logger is not None:
                self.security_event_logger(category="response_disclosure", outcome="replaced")
            return self._with_configuration_context(
                insufficient_info_response(question, safe_answer_text)
            )
        if answer_type is AnswerType.INSUFFICIENT:
            return self._with_configuration_context(
                insufficient_info_response(question, answer_text)
            )
        if answer_type is AnswerType.AMBIGUOUS:
            return self._with_configuration_context(
                ambiguous_answer(question, answer_text, tuple(evidence))
            )
        if answer_type is AnswerType.INCORRECT_PREMISE:
            return self._with_configuration_context(incorrect_premise_answer(question, answer_text))
        citations = self.citation_builder.build(
            evidence[: self.retrieval_config.final_top_k],
            supported_chunk_ids=self._supported_chunk_ids(payload.get("supported_chunk_ids")),
            available_document_ids=available_document_ids,
        )
        if answer_type is AnswerType.PARTIAL:
            return self._with_configuration_context(self.response_validator.validate(
                partial_answer(
                    question,
                    safe_answer_text,
                    citations,
                    self.llm_config.model,
                ),
                retrieved=evidence[: self.retrieval_config.final_top_k],
                available_document_ids=available_document_ids,
            ))
        answer = Answer(
            question=question,
            answer_text=safe_answer_text,
            answer_type=answer_type,
            citations=citations,
            model_used=self.llm_config.model,
        )
        return self._with_configuration_context(
            self.response_validator.validate(
                answer,
                retrieved=evidence[: self.retrieval_config.final_top_k],
                available_document_ids=available_document_ids,
            )
        )

    def _with_configuration_context(self, answer: Answer) -> Answer:
        embedding_config = getattr(self.retriever, "embedding_config", None)
        return replace(
            answer,
            llm_config_id=self.llm_config.config_id,
            embedding_config_id=getattr(embedding_config, "config_id", None),
            retrieval_config_id=self.retrieval_config.config_id,
        )

    async def _available_document_ids(
        self, results: tuple[VectorSearchResult, ...]
    ) -> Collection[UUID] | None:
        if self.document_repository is None:
            return None
        documents: list[Document | None] = []
        for document_id in {result.chunk.document_id for result in results}:
            try:
                documents.append(await self.document_repository.get(document_id))
            except DomainError:
                raise
            except Exception as exc:
                raise DatabaseUnavailableError(
                    "Document metadata is temporarily unavailable."
                ) from exc
        return {
            document.id
            for document in documents
            if document is not None and document.status.is_queryable
        }

    @staticmethod
    def _payload(raw: str) -> dict[str, object]:
        try:
            value = json.loads(raw)
        except json.JSONDecodeError:
            return {"answer_text": raw, "answer_type": "GROUNDED"}
        return value if isinstance(value, dict) else {"answer_text": raw}

    @staticmethod
    def _answer_type(value: object) -> AnswerType:
        try:
            return AnswerType(str(value))
        except ValueError:
            return AnswerType.GROUNDED

    @staticmethod
    def _supported_chunk_ids(value: object) -> tuple[UUID | str, ...]:
        if not isinstance(value, (list, tuple)):
            return ()
        return tuple(item for item in value if isinstance(item, (UUID, str)))
