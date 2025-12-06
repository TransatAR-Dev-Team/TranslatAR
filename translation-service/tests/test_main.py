from unittest.mock import AsyncMock, Mock, patch

import httpx
import pytest
from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def test_health_check():
    """
    Verifies the health endpoint returns 200.
    """
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "provider": "libretranslate"}


@pytest.mark.asyncio
async def test_translate_success():
    """
    Test valid translation request.
    """
    # Mock the response from LibreTranslate
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"translatedText": "Hola mundo"}

    with patch("main.httpx.AsyncClient") as MockClient:
        mock_instance = MockClient.return_value
        mock_instance.__aenter__.return_value = mock_instance
        mock_instance.post = AsyncMock(return_value=mock_response)

        payload = {"text": "Hello world", "source_lang": "en", "target_lang": "es"}
        response = client.post("/translate", json=payload)

        assert response.status_code == 200
        assert response.json() == {"translated_text": "Hola mundo"}

        # Verify the correct URL and payload were sent
        mock_instance.post.assert_called_once()
        args, kwargs = mock_instance.post.call_args
        assert "/translate" in args[0]
        assert kwargs["json"]["q"] == "Hello world"
        assert kwargs["json"]["source"] == "en"
        assert kwargs["json"]["target"] == "es"


@pytest.mark.asyncio
async def test_translate_connection_error():
    """
    Test handling of connection failures (503).
    """
    with patch("main.httpx.AsyncClient") as MockClient:
        mock_instance = MockClient.return_value
        mock_instance.__aenter__.return_value = mock_instance
        mock_instance.post = AsyncMock(
            side_effect=httpx.RequestError("Connection refused")
        )

        payload = {"text": "test", "source_lang": "en", "target_lang": "es"}
        response = client.post("/translate", json=payload)

        assert response.status_code == 503
        assert "Error connecting to translation engine" in response.json()["detail"]


@pytest.mark.asyncio
async def test_translate_backend_http_error():
    """
    Test handling of backend 500 errors.
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

        payload = {"text": "test", "source_lang": "en", "target_lang": "es"}
        response = client.post("/translate", json=payload)

        assert response.status_code == 500
        assert "Translation engine failed" in response.json()["detail"]


@pytest.mark.asyncio
async def test_translate_invalid_response_format():
    """
    Test handling of 200 OK but missing 'translatedText' key.
    """
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "error": "Something went wrong"
    }  # Missing expected key

    with patch("main.httpx.AsyncClient") as MockClient:
        mock_instance = MockClient.return_value
        mock_instance.__aenter__.return_value = mock_instance
        mock_instance.post = AsyncMock(return_value=mock_response)

        payload = {"text": "test", "source_lang": "en", "target_lang": "es"}
        response = client.post("/translate", json=payload)

        assert response.status_code == 500
        assert "Invalid response" in response.json()["detail"]


@pytest.mark.asyncio
async def test_translate_generic_exception():
    """
    Test handling of unexpected generic exceptions (e.g. memory error, library bug).
    This hits the final 'except Exception' block.
    """
    with patch("main.httpx.AsyncClient") as MockClient:
        mock_instance = MockClient.return_value
        mock_instance.__aenter__.return_value = mock_instance
        # Simulate a generic error that isn't an httpx error
        mock_instance.post = AsyncMock(side_effect=ValueError("Something exploded"))

        payload = {"text": "test", "source_lang": "en", "target_lang": "es"}
        response = client.post("/translate", json=payload)

        assert response.status_code == 500
        # Verify the detail message matches the f-string in the exception handler
        assert "An unexpected error occurred" in response.json()["detail"]
        assert "Something exploded" in response.json()["detail"]
