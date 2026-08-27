from l1_support_bot.application.evaluation.run_rag_evaluation import RunRagEvaluation
from l1_support_bot.domain.models.configuration import (
    ChunkingConfig,
    ConfigurationSnapshot,
    EmbeddingConfig,
    LLMConfig,
    RetrievalConfig,
)


class Executor:
    async def evaluate(self, cases, configuration):
        assert len(cases) == 1
        assert configuration.llm.model == "test-model"
        return {"recall_at_5": 1.0}, {"groundedness_rate": 1.0}


class Repository:
    def __init__(self) -> None:
        self.run = None

    async def save(self, run):
        self.run = run
        return run


def snapshot() -> ConfigurationSnapshot:
    return ConfigurationSnapshot(
        llm=LLMConfig(provider="test", model="test-model", endpoint="https://llm.test"),
        embedding=EmbeddingConfig(
            provider="test",
            model="test-embedding",
            model_version="1",
            endpoint="https://embedding.test",
            dimensions=3,
            index_compat_id="test:1:3",
        ),
        retrieval=RetrievalConfig(min_evidence_tokens=1),
        chunking=ChunkingConfig(),
    )


async def test_run_persists_metrics_and_non_secret_snapshot() -> None:
    repository = Repository()
    run = await RunRagEvaluation(executor=Executor(), repository=repository).execute(
        "dataset-1", ({"case_id": "one"},), snapshot()
    )

    assert repository.run is run
    assert run.retrieval_metrics["recall_at_5"] == 1.0
    assert run.configuration_snapshot["llm"]["model"] == "test-model"
    assert run.configuration_snapshot["dataset_version"] == "dataset-1"
    assert run.configuration_snapshot["prompt_version"] == "system_prompt_v1"
    assert run.configuration_snapshot["run_mode"] == "deterministic_fake"
    assert run.configuration_snapshot["captured_at"]
    assert "api_key" not in str(run.configuration_snapshot).lower()


async def test_run_snapshot_redacts_endpoint_credentials() -> None:
    repository = Repository()
    configuration = snapshot()
    configuration = ConfigurationSnapshot(
        llm=LLMConfig(
            provider=configuration.llm.provider,
            model=configuration.llm.model,
            endpoint="https://user:password@llm.test:443/v1?api_key=secret",
        ),
        embedding=configuration.embedding,
        retrieval=configuration.retrieval,
        chunking=configuration.chunking,
    )

    run = await RunRagEvaluation(executor=Executor(), repository=repository).execute(
        "dataset-1", ({"case_id": "one"},), configuration, run_mode="live_ollama"
    )

    assert run.configuration_snapshot["run_mode"] == "live_ollama"
    assert run.configuration_snapshot["llm"]["endpoint"] == "https://llm.test:443/v1"
    assert "password" not in str(run.configuration_snapshot)
    assert "secret" not in str(run.configuration_snapshot)
