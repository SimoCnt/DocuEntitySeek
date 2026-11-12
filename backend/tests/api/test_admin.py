import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.repositories.user_repository import UserRepository


def register_and_login(client: TestClient, *, email: str) -> dict[str, str]:
    password = "ValidPassword123!"

    register_response = client.post("/api/v1/auth/register", json={"email": email, "password": password})

    assert register_response.status_code == 201

    login_response = client.post("/api/v1/auth/token", data={"username": email, "password": password})

    token = login_response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.api
def test_normal_user_cannot_access_admin_users(client: TestClient) -> None:
    headers = register_and_login(client, email="user@example.com")
    response = client.get("/api/v1/admin/users", headers=headers)

    assert response.status_code == 403


@pytest.mark.api
def test_admin_can_list_users(client: TestClient, api_db_session: Session) -> None:
    headers = register_and_login(client, email="admin@example.com")
    user = UserRepository(api_db_session).get_by_email("admin@example.com")

    assert user is not None

    user.role = "ADMIN"
    api_db_session.commit()

    response = client.get("/api/v1/admin/users", headers=headers)

    assert response.status_code == 200

    users = response.json()
    assert len(users) == 1
    assert users[0]["role"] == "ADMIN"