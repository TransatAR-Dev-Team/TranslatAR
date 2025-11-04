import io
import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient, ASGITransport
from unittest.mock import AsyncMock, patch, MagicMock
from backend.main import app

client = TestClient(app)


def test_synchronous_pass():
    """
    A basic synchronous test to confirm pytest is working.
    """
    assert 1 + 1 == 2


@pytest.mark.asyncio
async def test_asynchronous_pass():
    """
    A basic asynchronous test to confirm pytest-asyncio is configured correctly.
    """
    assert "a" + "b" == "ab"


@pytest.mark.asyncio
async def test_get_history_no_google_id():
    """
    Unit test: endpoint returns empty history if googleId is missing.
    """
    response = client.post("/api/history/", data={})
    assert response.status_code == 200
    assert response.json() == {"history": []}


@pytest.mark.asyncio
@patch("backend.main.translations_collection.find")
async def test_get_history_db_exception(mock_collection):
    """
    Unit test: endpoint returns 500 if DB raises an exception.
    """
    mock_collection.side_effect = Exception("DB failure")
    response = client.post("/api/history/", data={"googleId": "abc123"})
    assert response.status_code == 500
    assert "Failed to retrieve history from database" in response.json()["detail"]