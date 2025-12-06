from unittest.mock import AsyncMock, Mock, patch

import httpx
import pytest
from fastapi.testclient import TestClient

from main import app

client = TestClient(app)

# --- Happy Path Tests ---


def test_health_check():
    """
    Verifies the health endpoint returns 200 and the model name.
    """
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert "model" in response.json()


@pytest.mark.asyncio
async def test_summarize_success_default_length():
    """
    Test that a valid request returns a summary.
    We mock httpx.AsyncClient so we don't actually hit Ollama.
    """
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"response": "This is a summary."}

    with patch("main.httpx.AsyncClient") as MockClient:
        mock_instance = MockClient.return_value
        mock_instance.__aenter__.return_value = mock_instance
        mock_instance.post = AsyncMock(return_value=mock_response)

        payload = {"text": "Long text content..."}
        response = client.post("/summarize", json=payload)

        assert response.status_code == 200
        assert response.json() == {"summary": "This is a summary."}


@pytest.mark.asyncio
async def test_summarize_success_short_length():
    """
    Test that specifying 'short' length changes the prompt instruction.
    """
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"response": "Short summary."}

    with patch("main.httpx.AsyncClient") as MockClient:
        mock_instance = MockClient.return_value
        mock_instance.__aenter__.return_value = mock_instance
        mock_instance.post = AsyncMock(return_value=mock_response)

        payload = {"text": "Long text content...", "length": "short"}
        response = client.post("/summarize", json=payload)

        assert response.status_code == 200

        # Check that the prompt instruction changed
        _, kwargs = mock_instance.post.call_args
        assert kwargs["json"]["prompt"].startswith(
            "Summarize the following text in one to two sentences"
        )


# --- Error Handling Tests ---


@pytest.mark.asyncio
async def test_summarize_ollama_connection_error():
    """
    Test that if Ollama is unreachable (RequestError), we return 503.
    """
    with patch("main.httpx.AsyncClient") as MockClient:
        mock_instance = MockClient.return_value
        mock_instance.__aenter__.return_value = mock_instance
        mock_instance.post = AsyncMock(side_effect=httpx.RequestError("Ollama down"))

        response = client.post("/summarize", json={"text": "test"})

        assert response.status_code == 503
        assert "Error connecting to Ollama" in response.json()["detail"]


@pytest.mark.asyncio
async def test_summarize_ollama_http_error():
    """
    Test that if Ollama returns a non-200 status code (e.g. 500), we return 500.
    """
    mock_response = Mock()
    mock_response.status_code = 500
    mock_response.text = "Internal Server Error"
    mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
        "Error", request=Mock(), response=mock_response
    )

    with patch("main.httpx.AsyncClient") as MockClient:
        mock_instance = MockClient.return_value
        mock_instance.__aenter__.return_value = mock_instance
        mock_instance.post = AsyncMock(return_value=mock_response)

        response = client.post("/summarize", json={"text": "test"})

        assert response.status_code == 500
        assert "Ollama failed" in response.json()["detail"]


@pytest.mark.asyncio
async def test_summarize_invalid_ollama_response():
    """
    Test case where Ollama returns 200 but the JSON is missing the 'response' key.
    """
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"wrong_key": "some value"}

    with patch("main.httpx.AsyncClient") as MockClient:
        mock_instance = MockClient.return_value
        mock_instance.__aenter__.return_value = mock_instance
        mock_instance.post = AsyncMock(return_value=mock_response)

        response = client.post("/summarize", json={"text": "test"})

        assert response.status_code == 500
        assert "Invalid response from Ollama" in response.json()["detail"]


@pytest.mark.asyncio
async def test_summarize_generic_exception():
    """
    Test handling of unexpected generic exceptions to cover the final 'except Exception' block.
    """
    with patch("main.httpx.AsyncClient") as MockClient:
        mock_instance = MockClient.return_value
        mock_instance.__aenter__.return_value = mock_instance
        # Simulate a generic Python error (not an httpx error)
        mock_instance.post = AsyncMock(
            side_effect=ValueError("Unexpected crash inside logic")
        )

        response = client.post("/summarize", json={"text": "test"})

        assert response.status_code == 500
        # Check that it fell through to the generic handler
        assert "An unexpected error occurred" in response.json()["detail"]
