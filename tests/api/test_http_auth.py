from urllib.parse import urlsplit, urlunsplit
from uuid import uuid4

from fastapi.testclient import TestClient

from main import app
from src.database.base import initialize_database


def test_authentication_http_flow(tmp_path, monkeypatch):
    # Always use the isolated PostgreSQL test database.
    configured_url = urlsplit(
        __import__("src.database.session", fromlist=["get_database_url"])
        .get_database_url()
    )
    test_url = urlunsplit(
        (
            configured_url.scheme,
            configured_url.netloc,
            "/ai_hub_test",
            configured_url.query,
            configured_url.fragment,
        )
    )
    monkeypatch.setenv("AI_HUB_DATABASE_URL", test_url)
    monkeypatch.setenv(
        "AI_HUB_SECRET_KEY",
        "ai-hub-http-test-secret-key-at-least-32-characters",
    )

    initialize_database()

    unique_id = uuid4().hex[:12]
    registration = {
        "username": f"http_test_{unique_id}",
        "email": f"http_test_{unique_id}@example.test",
        "password": "Strong-Test-Password-2026",
    }

    with TestClient(app) as client:
        response = client.post("/api/v1/auth/register", json=registration)
        assert response.status_code == 201, response.text

        registered = response.json()
        assert registered["username"] == registration["username"]
        assert "password_hash" not in registered

        response = client.post("/api/v1/auth/register", json=registration)
        assert response.status_code == 409, response.text

        response = client.post(
            "/api/v1/auth/login",
            json={
                "username": registration["username"],
                "password": registration["password"],
            },
        )
        assert response.status_code == 200, response.text

        token_data = response.json()
        assert token_data["token_type"] == "bearer"
        assert token_data["access_token"]

        headers = {
            "Authorization": f"Bearer {token_data['access_token']}"
        }
        response = client.get("/api/v1/users/me", headers=headers)
        assert response.status_code == 200, response.text

        profile = response.json()
        assert profile["username"] == registration["username"]
        assert "password_hash" not in profile

        response = client.get("/api/v1/users/me")
        assert response.status_code == 401, response.text

        response = client.post(
            "/api/v1/auth/login",
            json={
                "username": registration["username"],
                "password": "Wrong-Test-Password-2026",
            },
        )
        assert response.status_code == 401, response.text

        response = client.get("/health")
        assert response.status_code == 200, response.text
        assert response.json()["status"] == "healthy"
