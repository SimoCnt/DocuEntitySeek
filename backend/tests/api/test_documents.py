import pytest
from fastapi.testclient import TestClient


PDF_BYTES = b"%PDF-1.7\n1 0 obj\n<<>>\nendobj\n%%EOF\n"


def register_and_login(client: TestClient, *, email: str) -> dict[str, str]:
    password = "ValidPassword123!"

    register_response = client.post("/api/v1/auth/register", json={"email": email, "password": password})

    assert register_response.status_code == 201

    login_response = client.post("/api/v1/auth/token", data={"username": email, "password": password})

    assert login_response.status_code == 200

    token = login_response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.api
def test_documents_require_authentication(client: TestClient) -> None:
    response = client.get("/api/v1/documents")
    assert response.status_code == 401


@pytest.mark.api
def test_create_document(client: TestClient) -> None:
    headers = register_and_login(client, email="owner@example.com")

    response = client.post(
        "/api/v1/documents",
        headers=headers,
        files={"file": ("document.pdf", PDF_BYTES, "application/pdf")},
        data={"category": "DISCIPLINARE"},
    )

    assert response.status_code == 201

    body = response.json()
    assert body["name"] == "document.pdf"
    assert body["category"] == "DISCIPLINARE"
    assert body["status"] == "PROCESSING"


@pytest.mark.api
def test_created_document_is_listed(client: TestClient) -> None:
    headers = register_and_login(client, email="owner@example.com")

    create_response = client.post(
        "/api/v1/documents",
        headers=headers,
        files={"file": ("document.pdf", PDF_BYTES, "application/pdf")},
        data={"category": "DISCIPLINARE"},
    )

    document_id = create_response.json()["id"]
    list_response = client.get("/api/v1/documents", headers=headers)

    assert list_response.status_code == 200

    documents = list_response.json()
    assert len(documents) == 1
    assert documents[0]["id"] == document_id


@pytest.mark.api
def test_user_cannot_access_another_users_document(client: TestClient) -> None:
    user_a_headers = register_and_login(client, email="a@example.com")
    user_b_headers = register_and_login(client, email="b@example.com")

    create_response = client.post(
        "/api/v1/documents",
        headers=user_a_headers,
        files={"file": ("private.pdf", PDF_BYTES, "application/pdf")},
        data={"category": "DISCIPLINARE"},
    )

    document_id = create_response.json()["id"]

    response = client.get(
        f"/api/v1/documents/{document_id}",
        headers=user_b_headers,
    )

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "DOCUMENT_NOT_FOUND"


@pytest.mark.api
def test_invalid_pdf_returns_400(client: TestClient) -> None:
    headers = register_and_login(client, email="owner@example.com")

    response = client.post(
        "/api/v1/documents",
        headers=headers,
        files={"file": ("fake.pdf", b"this is not a pdf", "application/pdf")},
        data={"category": "DISCIPLINARE"},
    )

    assert response.status_code == 400
    assert response.json()["error"]["code"] == "INVALID_DOCUMENT_FILE"


@pytest.mark.api
def test_invalid_document_uuid_returns_422(client: TestClient) -> None:
    headers = register_and_login(client, email="owner@example.com")
    response = client.get("/api/v1/documents/pippo", headers=headers)

    assert response.status_code == 422