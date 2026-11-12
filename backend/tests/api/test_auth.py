import pytest
from fastapi.testclient import TestClient


@pytest.mark.api
def test_register_user(client: TestClient) -> None:
    response = client.post("/api/v1/auth/register", json={"email": "user@example.com", "password": "ValidPassword123!"})

    assert response.status_code == 201

    body = response.json()
    assert body["email"] == "user@example.com"
    assert body["role"] == "USER"
    assert body["plan"]["code"] == "BASE"
    assert body["isActive"] is True
    assert "password" not in body
    assert "passwordHash" not in body


@pytest.mark.api
def test_duplicate_registration_returns_409(client: TestClient) -> None:
    payload = {"email": "duplicate@example.com", "password": "ValidPassword123!"}

    first = client.post("/api/v1/auth/register", json=payload)
    second = client.post("/api/v1/auth/register", json=payload)

    assert first.status_code == 201
    assert second.status_code == 409
    assert second.json()["error"]["code"] == "EMAIL_ALREADY_REGISTERED" 


@pytest.mark.api
def test_login_returns_access_token(client: TestClient) -> None:
    client.post("/api/v1/auth/register", json={"email": "login@example.com", "password": "ValidPassword123!"})

    response = client.post("/api/v1/auth/token", data={"username": "login@example.com", "password": "ValidPassword123!"})

    assert response.status_code == 200

    body = response.json()
    assert body["token_type"] == "bearer"
    assert body["access_token"]
    assert body["expires_in"] == 1800


@pytest.mark.api
def test_wrong_password_returns_401(client: TestClient) -> None:
    client.post("/api/v1/auth/register", json={"email": "login@example.com", "password": "ValidPassword123!"})

    response = client.post("/api/v1/auth/token", data={"username": "login@example.com", "password": "WrongPassword123!"})

    assert response.status_code == 401
    assert response.json()["error"]["code"] == "AUTHENTICATION_ERROR"


@pytest.mark.api
def test_current_user(client: TestClient) -> None:
    client.post("/api/v1/auth/register", json={"email": "me@example.com", "password": "ValidPassword123!"})

    login_response = client.post("/api/v1/auth/token", data={"username": "me@example.com", "password": "ValidPassword123!"})

    token = login_response.json()["access_token"]

    response = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 200
    assert response.json()["email"] == "me@example.com"