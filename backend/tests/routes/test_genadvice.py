from unittest.mock import AsyncMock, Mock, patch

import httpx
import pytest
from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


@pytest.mark.asyncio
async def test_get_advice_success():
    """Test that a valid request returns 200 OK and the expected advice text."""

    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"advice": "Keep practicing!"}

    with patch("routes.genadvice.httpx.AsyncClient") as MockClient:
        mock_instance = MockClient.return_value
        mock_instance.__aenter__.return_value = mock_instance
        mock_instance.post = AsyncMock(return_value=mock_response)

        response = client.post("/api/advice", json={"text": "Hello world"})

        assert response.status_code == 200
        assert response.json() == {"advice": "Keep practicing!"}


@pytest.mark.asyncio
async def test_get_advice_generation_failed():
    """
    Test that the endpoint returns 500 if the downstream service response is missing the 'advice'
    key.
    """
    mock_response = Mock()
    mock_response.status_code = 200
    # Return JSON but missing the 'advice' key
    mock_response.json.return_value = {"other_field": "no advice here"}

    with patch("routes.genadvice.httpx.AsyncClient") as MockClient:
        mock_instance = MockClient.return_value
        mock_instance.__aenter__.return_value = mock_instance
        mock_instance.post = AsyncMock(return_value=mock_response)

        response = client.post("/api/advice", json={"text": "Hello"})

        # The code raises HTTPException(500, "Advice generation failed")
        # BUT, it is currently caught by the generic 'except Exception' block
        # so it gets re-raised as "Error during advice generation: ..."
        assert response.status_code == 500
        assert "Advice generation failed" in response.json()["detail"]


@pytest.mark.asyncio
async def test_get_advice_exception_handling():
    """Test that network errors or unexpected exceptions are caught and wrapped in a 500 error."""
    with patch("routes.genadvice.httpx.AsyncClient") as MockClient:
        mock_instance = MockClient.return_value
        mock_instance.__aenter__.return_value = mock_instance
        # Simulate a network crash
        mock_instance.post = AsyncMock(side_effect=httpx.RequestError("Connection refused"))

        response = client.post("/api/advice", json={"text": "Hello"})

        assert response.status_code == 500
        assert "Error during advice generation" in response.json()["detail"]
        assert "Connection refused" in response.json()["detail"]
