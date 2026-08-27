from fastapi.testclient import TestClient

from l1_support_bot.interface.api.main import create_app


def test_app_registers_versioned_health_route() -> None:
    client = TestClient(create_app())

    response = client.get("/api/v1/health")

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "healthy"
    assert payload["version"] == "0.1.0"
    assert response.headers["x-request-id"]
    assert response.headers["x-correlation-id"]


def test_unknown_route_uses_common_error_shape() -> None:
    response = TestClient(create_app()).get("/api/v1/missing")

    assert response.status_code == 404
    assert set(response.json()) >= {"error_code", "message", "request_id", "timestamp", "details"}