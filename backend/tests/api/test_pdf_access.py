"""GET PDF: controllo proprietario e supporto HTTP Range."""
from fastapi.testclient import TestClient


def headers(client: TestClient, email: str) -> dict[str, str]:
    password = "ValidPassword123!"
    registration = client.post("/api/v1/auth/register", json={"email": email, "password": password})
    assert registration.status_code == 201
    login = client.post("/api/v1/auth/token", data={"username": email, "password": password})
    assert login.status_code == 200
    return {"Authorization": f"Bearer {login.json()['access_token']}"}


def test_pdf_is_private_and_supports_ranges(client: TestClient):
    owner = headers(client, "pdf-owner@example.com")
    other = headers(client, "pdf-other@example.com")
    content = b"%PDF-1.7\ntest\n%%EOF"
    created = client.post("/api/v1/documents", headers=owner, files={"file": ("test.pdf", content, "application/pdf")})
    assert created.status_code == 201
    doc_id = created.json()["id"]
    url = f"/api/v1/documents/{doc_id}/file"
    assert client.get(url).status_code == 401
    assert client.get(url, headers=other).status_code == 404
    full = client.get(url, headers=owner)
    assert full.status_code == 200
    assert full.content == content
    assert full.headers["content-type"].startswith("application/pdf")
    partial = client.get(url, headers={**owner, "Range": "bytes=0-3"})
    assert partial.status_code == 206
    assert partial.content == b"%PDF"
    assert partial.headers["content-range"] == f"bytes 0-3/{len(content)}"
    invalid = client.get(url, headers={**owner, "Range": "bytes=9999-"})
    assert invalid.status_code == 416
