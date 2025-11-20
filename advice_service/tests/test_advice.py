import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock, Mock
from main import app

client = TestClient(app)


def test_advice_endpoint_success():
    with patch("main.httpx.AsyncClient") as mock_client:
        mock_instance = mock_client.return_value.__aenter__.return_value

        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_response.json = Mock(return_value={"response": "Mock advice here."})

        mock_instance.post.return_value = mock_response

        response = client.post("/advice", json={"text": "Hello, how was your day?"})
        assert response.status_code == 200
        data = response.json()
        assert "advice" in data
        assert data["advice"] == "Mock advice here."


def test_advice_endpoint_missing_response():
    with patch("main.httpx.AsyncClient") as mock_client:
        mock_instance = mock_client.return_value.__aenter__.return_value

        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_response.json = Mock(return_value={"unexpected": "value"})

        mock_instance.post.return_value = mock_response

        response = client.post("/advice", json={"text": "Hello"})
        assert response.status_code == 500
        assert "invalid" in response.json()["detail"].lower()


def test_advice_endpoint_ollama_exception():
    with patch("main.httpx.AsyncClient") as mock_client:
        # mock the context manager __aenter__
        mock_instance = mock_client.return_value.__aenter__.return_value

        # make post() raise an exception
        mock_instance.post = AsyncMock(side_effect=Exception("Ollama server error"))

        response = client.post("/advice", json={"text": "Hello"})

        assert response.status_code == 500
        assert "error" in response.json()["detail"].lower()
