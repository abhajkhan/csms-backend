"""Health check endpoint tests."""

from fastapi.testclient import TestClient


def test_health_check(client: TestClient) -> None:
    """GET /health must return 200 with status=healthy."""
    response = client.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "healthy"
    assert "project" in body


def test_root(client: TestClient) -> None:
    """GET / must return 200 with project metadata."""
    response = client.get("/")
    assert response.status_code == 200
    body = response.json()
    assert "project" in body
    assert "version" in body
    assert "docs" in body
