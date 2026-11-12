import pytest
from fastapi.testclient import TestClient


@pytest.mark.api
def test_health_endpoint(client: TestClient) -> None:
    response = client.get("/api/v1/health")

    assert response.status_code == 200

    body = response.json()
    assert body["status"] == "ok"


@pytest.mark.api
def test_database_health_uses_test_database(client: TestClient) -> None:
    response = client.get("/api/v1/health/database")

    assert response.status_code == 200

    body = response.json()
    assert body["database"] == "docuentityseek_test"
    assert body["user"] == "docuentityseek_test_app"