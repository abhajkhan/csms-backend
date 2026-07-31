"""Health check endpoint tests."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_health_check(client: AsyncClient) -> None:
    """GET /health must return 200 with status=healthy."""
    response = await client.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "healthy"
    assert "project" in body


@pytest.mark.asyncio
async def test_root(client: AsyncClient) -> None:
    """GET / must return 200 with project metadata."""
    response = await client.get("/")
    assert response.status_code == 200
    body = response.json()
    assert "project" in body
    assert "version" in body
    assert "docs" in body
