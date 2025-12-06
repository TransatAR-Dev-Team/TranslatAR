from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient
from pymongo.errors import ConnectionFailure

from main import app

client = TestClient(app)


@pytest.mark.asyncio
async def test_verbose_health_check_success():
    """Test verbose health check returns 200 when DB is connected."""
    # Mock the mongodb client used in routes.health
    with patch("routes.health.client") as mock_client:
        # Mock the admin command to return success
        mock_client.admin.command = AsyncMock(return_value={"ok": 1.0})

        response = client.get("/api/health")

        assert response.status_code == 200
        assert response.json() == {"status": "ok", "database_status": "connected"}
        # Verify ping was called
        mock_client.admin.command.assert_awaited_once_with("ping")


@pytest.mark.asyncio
async def test_verbose_health_check_failure():
    """Test verbose health check returns 503 when DB connection fails."""
    with patch("routes.health.client") as mock_client:
        # Mock the admin command to raise ConnectionFailure
        mock_client.admin.command = AsyncMock(side_effect=ConnectionFailure("DB down"))

        response = client.get("/api/health")

        # Verify 503 and error message
        assert response.status_code == 503
        assert response.json()["detail"] == "Database connection is unhealthy."


@pytest.mark.asyncio
async def test_silent_health_check_success():
    """Test silent health check returns 200 when DB is connected."""
    with patch("routes.health.client") as mock_client:
        mock_client.admin.command = AsyncMock(return_value={"ok": 1.0})

        response = client.get("/api/health/silent")

        assert response.status_code == 200
        assert response.json() == {"status": "ok", "database_status": "connected"}


@pytest.mark.asyncio
async def test_silent_health_check_failure():
    """Test silent health check returns 503 when DB connection fails."""
    with patch("routes.health.client") as mock_client:
        mock_client.admin.command = AsyncMock(side_effect=ConnectionFailure("DB down"))

        response = client.get("/api/health/silent")

        assert response.status_code == 503
        assert response.json()["detail"] == "Database connection is unhealthy."
