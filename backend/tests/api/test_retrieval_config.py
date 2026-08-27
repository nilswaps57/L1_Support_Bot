from fastapi.testclient import TestClient

from l1_support_bot.interface.api.main import create_app
from l1_support_bot.interface.dependencies import PortDependencies


def test_retrieval_config_defaults_keep_reranking_disabled() -> None:
    response = TestClient(create_app(dependencies=PortDependencies())).get(
        "/api/v1/config/retrieval"
    )

    assert response.status_code == 200
    assert response.json()["rerank_enabled"] is False
    assert response.json()["dense_weight"] == 0.7
    assert response.json()["sparse_weight"] == 0.3
