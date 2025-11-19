import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock
from main import app

client = TestClient(app)

def test_advice_endpoint_sync():
    """Test the /advice endpoint synchronously with a mock request."""
    with patch("main.httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {"response": "Mock advice here."}

        response = client.post("/advice", json={"text": "Hello, how was your day?"})
        assert response.status_code == 200
        data = response.json()
        assert "advice" in data
        assert data["advice"] == "Mock advice here."


@pytest.mark.asyncio
async def test_advice_endpoint_async_error():
    """Test that /advice handles exceptions from Ollama."""
    with patch("main.httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.side_effect = Exception("Ollama server error")

        response = client.post("/advice", json={"text": "Hello, how was your day?"})
        assert response.status_code == 503
        assert "Ollama" in response.json()["detail"]
