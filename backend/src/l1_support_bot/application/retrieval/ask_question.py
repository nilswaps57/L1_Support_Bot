"""Generate a grounded answer from retrieved evidence only."""

from __future__ import annotations

import json

from l1_support_bot.application.retrieval.prompt_builder import PromptBuilder
from l1_support_bot.domain.models.answer import Answer, AnswerType
from l1_support_bot.domain.models.citation import Citation
from l1_support_bot.domain.models.configuration import LLMConfig, RetrievalConfig
from l1_support_bot.domain.ports.llm import LLMPort
from l1_support_bot.domain.ports.retrieval import RetrieverPort
from l1_support_bot.domain.ports.vector_store import VectorSearchResult


class AskQuestion:
    def __init__(
        self,
        *,
        retriever: RetrieverPort,
        llm: LLMPort,
        llm_config: LLMConfig,
        retrieval_config: RetrievalConfig | None = None,
        prompt_builder: PromptBuilder | None = None,
    ) -> None:
        self.retriever = retriever
        self.llm = llm
        self.llm_config = llm_config
        self.retrieval_config = retrieval_config or RetrievalConfig()
        self.prompt_builder = prompt_builder or PromptBuilder()

    async def execute(self, question: str) -> Answer:
        results = await self.retriever.retrieve(
            question,
            limit=self.retrieval_config.top_k_candidates,
            config=self.retrieval_config,
        )
        evidence = tuple(
            result
            for result in results
            if result.score >= self.retrieval_config.similarity_threshold
        )
        if not evidence:
            return Answer(
                question=question,
                answer_text=(
                    "The available knowledge sources do not contain sufficient information "
                    "to answer this question."
                ),
                answer_type=AnswerType.INSUFFICIENT,
                insufficient_information=True,
            )
        prompt = self.prompt_builder.build(
            question, tuple(evidence[: self.retrieval_config.final_top_k])
        )
        raw = await self.llm.complete(prompt, config=self.llm_config)
        payload = self._payload(raw)
        answer_type = self._answer_type(payload.get("answer_type"))
        if answer_type is AnswerType.INSUFFICIENT:
            return Answer(
                question=question,
                answer_text=str(
                    payload.get("answer_text")
                    or "The available knowledge sources do not contain sufficient information "
                    "to answer this question."
                ),
                answer_type=answer_type,
                insufficient_information=True,
            )
        citations = tuple(
            self._citation(result)
            for result in evidence[: self.retrieval_config.final_top_k]
        )
        return Answer(
            question=question,
            answer_text=str(payload.get("answer_text") or raw),
            answer_type=answer_type,
            citations=citations,
            model_used=self.llm_config.model,
        )

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
    def _citation(result: VectorSearchResult) -> Citation:
        metadata = result.chunk.metadata
        return Citation(
            chunk_id=result.chunk.id,
            document_id=result.chunk.document_id,
            document_name=metadata.document_name,
            page_number=metadata.page_number,
            section=metadata.section,
            task_code=metadata.task_code,
            screen_name=metadata.screen_name,
            error_code=metadata.error_code,
            jira_id=metadata.jira_id,
            source_type=metadata.source_type,
            relevance_score=result.score,
        )
