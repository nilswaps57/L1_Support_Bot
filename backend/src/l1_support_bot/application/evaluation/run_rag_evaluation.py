"""Orchestrate a RAG evaluation and persist its configuration snapshot."""

from collections.abc import Mapping, Sequence
from datetime import UTC, datetime
from typing import Protocol
from urllib.parse import urlsplit, urlunsplit

from l1_support_bot.domain.models.configuration import ConfigurationSnapshot
from l1_support_bot.domain.models.evaluation import EvaluationRun
from l1_support_bot.domain.ports.evaluation_repository import EvaluationRepository


class RagEvaluationExecutor(Protocol):
    async def evaluate(
        self,
        cases: Sequence[Mapping[str, object]],
        configuration: ConfigurationSnapshot,
    ) -> tuple[Mapping[str, object], Mapping[str, object]]: ...


class RunRagEvaluation:
    def __init__(
        self,
        *,
        executor: RagEvaluationExecutor,
        repository: EvaluationRepository,
    ) -> None:
        self.executor = executor
        self.repository = repository

    async def execute(
        self,
        dataset_id: str,
        cases: Sequence[Mapping[str, object]],
        configuration: ConfigurationSnapshot,
        *,
        dataset_version: str | None = None,
        prompt_version: str = "system_prompt_v1",
        run_mode: str = "deterministic_fake",
    ) -> EvaluationRun:
        retrieval_metrics, generation_metrics = await self.executor.evaluate(cases, configuration)
        run = EvaluationRun(
            dataset_id=dataset_id,
            configuration_snapshot=_snapshot(
                configuration,
                dataset_version=dataset_version or dataset_id,
                prompt_version=prompt_version,
                run_mode=run_mode,
            ),
            retrieval_metrics=retrieval_metrics,
            generation_metrics=generation_metrics,
        )
        return await self.repository.save(run)


def _safe_endpoint(endpoint: str) -> str:
    parsed = urlsplit(endpoint)
    hostname = parsed.hostname or ""
    if parsed.port is not None:
        hostname = f"{hostname}:{parsed.port}"
    return urlunsplit((parsed.scheme, hostname, parsed.path, "", ""))


def _snapshot(
    configuration: ConfigurationSnapshot,
    *,
    dataset_version: str,
    prompt_version: str,
    run_mode: str,
) -> dict[str, object]:
    return {
        "captured_at": datetime.now(UTC).isoformat(),
        "dataset_version": dataset_version,
        "prompt_version": prompt_version,
        "run_mode": run_mode,
        "llm": {
            "provider": configuration.llm.provider,
            "model": configuration.llm.model,
            "endpoint": _safe_endpoint(configuration.llm.endpoint),
            "temperature": configuration.llm.temperature,
            "max_tokens": configuration.llm.max_tokens,
            "context_window": configuration.llm.context_window,
            "timeout_seconds": configuration.llm.timeout_seconds,
            "max_retries": configuration.llm.max_retries,
        },
        "embedding": {
            "provider": configuration.embedding.provider,
            "model": configuration.embedding.model,
            "model_version": configuration.embedding.model_version,
            "endpoint": _safe_endpoint(configuration.embedding.endpoint),
            "dimensions": configuration.embedding.dimensions,
            "index_compat_id": configuration.embedding.index_compat_id,
            "distance_method": configuration.embedding.distance_method,
            "batch_size": configuration.embedding.batch_size,
            "timeout_seconds": configuration.embedding.timeout_seconds,
        },
        "retrieval": {
            "top_k_candidates": configuration.retrieval.top_k_candidates,
            "final_top_k": configuration.retrieval.final_top_k,
            "similarity_threshold": configuration.retrieval.similarity_threshold,
            "dense_weight": configuration.retrieval.dense_weight,
            "sparse_weight": configuration.retrieval.sparse_weight,
            "rerank_enabled": configuration.retrieval.rerank_enabled,
        },
        "chunking": {
            "strategy": configuration.chunking.strategy,
            "target_chunk_tokens": configuration.chunking.target_chunk_tokens,
            "max_chunk_tokens": configuration.chunking.max_chunk_tokens,
            "overlap_tokens": configuration.chunking.overlap_tokens,
        },
    }
