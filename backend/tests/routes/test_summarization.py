from datetime import UTC, datetime
from unittest.mock import AsyncMock

import httpx
import pytest
from fastapi.testclient import TestClient

from main import app
from routes import summarization as summarization_route

# --- Fixtures ---


@pytest.fixture
def client() -> TestClient:
    """Provides a test client for the FastAPI application."""
    return TestClient(app)


# --- Tests for POST /api/summarize ---


def test_summarize_success_default_length(client, monkeypatch):
    """
    Test successful summarization with default length parameter.
    """
    monkeypatch.setattr(
        summarization_route, "SUMMARIZATION_SERVICE_URL", "http://summarization:9002"
    )

    # Mock the httpx.AsyncClient
    class MockResponse:
        status_code = 200

        def raise_for_status(self):
            pass

        def json(self):
            return {"summary": "This is a test summary"}

    class MockClient:
        async def __aenter__(self):
            return self

        async def __aexit__(self, *args):
            pass

        async def post(self, url, json=None, **kwargs):
            # Verify the correct payload was sent
            assert json["text"] == "This is a long text that needs summarization."
            assert json["length"] == "medium"  # default
            return MockResponse()

    monkeypatch.setattr("routes.summarization.httpx.AsyncClient", lambda timeout: MockClient())

    response = client.post(
        "/api/summarize",
        json={"text": "This is a long text that needs summarization."},
    )

    assert response.status_code == 200
    data = response.json()
    assert "summary" in data
    assert data["summary"] == "This is a test summary"


def test_summarize_success_short_length(client, monkeypatch):
    """
    Test successful summarization with 'short' length parameter.
    """
    monkeypatch.setattr(
        summarization_route, "SUMMARIZATION_SERVICE_URL", "http://summarization:9002"
    )

    class MockResponse:
        status_code = 200

        def raise_for_status(self):
            pass

        def json(self):
            return {"summary": "Brief summary"}

    class MockClient:
        async def __aenter__(self):
            return self

        async def __aexit__(self, *args):
            pass

        async def post(self, url, json=None, **kwargs):
            assert json["length"] == "short"
            return MockResponse()

    monkeypatch.setattr("routes.summarization.httpx.AsyncClient", lambda timeout: MockClient())

    response = client.post(
        "/api/summarize",
        json={"text": "Long text here.", "length": "short"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["summary"] == "Brief summary"


def test_summarize_success_long_length(client, monkeypatch):
    """
    Test successful summarization with 'long' length parameter.
    """
    monkeypatch.setattr(
        summarization_route, "SUMMARIZATION_SERVICE_URL", "http://summarization:9002"
    )

    class MockResponse:
        status_code = 200

        def raise_for_status(self):
            pass

        def json(self):
            return {"summary": "This is a much longer and more detailed summary of the text."}

    class MockClient:
        async def __aenter__(self):
            return self

        async def __aexit__(self, *args):
            pass

        async def post(self, url, json=None, **kwargs):
            assert json["length"] == "long"
            return MockResponse()

    monkeypatch.setattr("routes.summarization.httpx.AsyncClient", lambda timeout: MockClient())

    response = client.post(
        "/api/summarize",
        json={"text": "Long text here.", "length": "long"},
    )

    assert response.status_code == 200


def test_summarize_missing_text_field(client):
    """
    Test that the endpoint returns 422 when the 'text' field is missing.
    """
    response = client.post("/api/summarize", json={"length": "medium"})

    assert response.status_code == 422


def test_summarize_empty_text(client, monkeypatch):
    """
    Test summarization with empty text string.
    The service should handle this, but we verify the request is made.
    """
    monkeypatch.setattr(
        summarization_route, "SUMMARIZATION_SERVICE_URL", "http://summarization:9002"
    )

    class MockResponse:
        status_code = 200

        def raise_for_status(self):
            pass

        def json(self):
            return {"summary": ""}

    class MockClient:
        async def __aenter__(self):
            return self

        async def __aexit__(self, *args):
            pass

        async def post(self, url, json=None, **kwargs):
            assert json["text"] == ""
            return MockResponse()

    monkeypatch.setattr("routes.summarization.httpx.AsyncClient", lambda timeout: MockClient())

    response = client.post("/api/summarize", json={"text": ""})

    assert response.status_code == 200
    assert response.json()["summary"] == ""


def test_summarize_service_returns_none(client, monkeypatch):
    """
    Test that the endpoint returns 500 when the summarization service
    returns a response without a 'summary' field.
    """
    monkeypatch.setattr(
        summarization_route, "SUMMARIZATION_SERVICE_URL", "http://summarization:9002"
    )

    class MockResponse:
        status_code = 200

        def raise_for_status(self):
            pass

        def json(self):
            return {}  # Missing 'summary' field

    class MockClient:
        async def __aenter__(self):
            return self

        async def __aexit__(self, *args):
            pass

        async def post(self, url, json=None, **kwargs):
            return MockResponse()

    monkeypatch.setattr("routes.summarization.httpx.AsyncClient", lambda timeout: MockClient())

    response = client.post("/api/summarize", json={"text": "Test text"})

    assert response.status_code == 500
    assert "Summarization failed" in response.json()["detail"]


def test_summarize_service_http_error(client, monkeypatch):
    """
    Test that the endpoint returns 500 when the summarization service
    returns an HTTP error.
    """
    monkeypatch.setattr(
        summarization_route, "SUMMARIZATION_SERVICE_URL", "http://summarization:9002"
    )

    class MockClient:
        async def __aenter__(self):
            return self

        async def __aexit__(self, *args):
            pass

        async def post(self, url, json=None, **kwargs):
            raise httpx.HTTPError("Service unavailable")

    monkeypatch.setattr("routes.summarization.httpx.AsyncClient", lambda timeout: MockClient())

    response = client.post("/api/summarize", json={"text": "Test text"})

    assert response.status_code == 500
    assert "Error during summarization" in response.json()["detail"]


def test_summarize_service_timeout(client, monkeypatch):
    """
    Test that the endpoint handles timeout errors from the summarization service.
    """
    monkeypatch.setattr(
        summarization_route, "SUMMARIZATION_SERVICE_URL", "http://summarization:9002"
    )

    class MockClient:
        async def __aenter__(self):
            return self

        async def __aexit__(self, *args):
            pass

        async def post(self, url, json=None, **kwargs):
            raise httpx.TimeoutException("Request timed out")

    monkeypatch.setattr("routes.summarization.httpx.AsyncClient", lambda timeout: MockClient())

    response = client.post("/api/summarize", json={"text": "Test text"})

    assert response.status_code == 503
    assert "unavailable" in response.json()["detail"]


def test_summarize_service_500_response(client, monkeypatch):
    """
    Test that the endpoint handles 500 responses from the summarization service.
    """
    monkeypatch.setattr(
        summarization_route, "SUMMARIZATION_SERVICE_URL", "http://summarization:9002"
    )

    class MockResponse:
        status_code = 500
        text = "Mocked internal server error from downstream service"

        def raise_for_status(self):
            raise httpx.HTTPStatusError(
                "Internal Server Error",
                request=None,
                response=self,
            )

        def json(self):
            return {"error": "Internal server error"}

    class MockClient:
        async def __aenter__(self):
            return self

        async def __aexit__(self, *args):
            pass

        async def post(self, url, json=None, **kwargs):
            return MockResponse()

    monkeypatch.setattr("routes.summarization.httpx.AsyncClient", lambda timeout: MockClient())

    response = client.post("/api/summarize", json={"text": "Test text"})

    assert response.status_code == 500


def test_summarize_special_characters(client, monkeypatch):
    """
    Test summarization with text containing special characters and unicode.
    """
    monkeypatch.setattr(
        summarization_route, "SUMMARIZATION_SERVICE_URL", "http://summarization:9002"
    )

    special_text = "Hello! 你好 🌍 émoji & symbols: @#$%"

    class MockResponse:
        status_code = 200

        def raise_for_status(self):
            pass

        def json(self):
            return {"summary": "Summary with special chars"}

    class MockClient:
        async def __aenter__(self):
            return self

        async def __aexit__(self, *args):
            pass

        async def post(self, url, json=None, **kwargs):
            assert special_text in json["text"]
            return MockResponse()

    monkeypatch.setattr("routes.summarization.httpx.AsyncClient", lambda timeout: MockClient())

    response = client.post("/api/summarize", json={"text": special_text})

    assert response.status_code == 200


def test_summarize_invalid_length_value(client, monkeypatch):
    """
    Test that the endpoint accepts any string for length parameter.
    The summarization service will handle validation.
    """
    monkeypatch.setattr(
        summarization_route, "SUMMARIZATION_SERVICE_URL", "http://summarization:9002"
    )

    class MockResponse:
        status_code = 200

        def raise_for_status(self):
            pass

        def json(self):
            return {"summary": "Summary"}

    class MockClient:
        async def __aenter__(self):
            return self

        async def __aexit__(self, *args):
            pass

        async def post(self, url, json=None, **kwargs):
            # Service receives whatever length value was sent
            assert json["length"] == "invalid_value"
            return MockResponse()

    monkeypatch.setattr("routes.summarization.httpx.AsyncClient", lambda timeout: MockClient())

    response = client.post(
        "/api/summarize",
        json={"text": "Test", "length": "invalid_value"},
    )

    # The endpoint doesn't validate length values, passes them through
    assert response.status_code == 200


def test_summarize_timeout_configuration(client, monkeypatch):
    """
    Test that the summarization request uses the correct timeout (120 seconds).
    """
    monkeypatch.setattr(
        summarization_route, "SUMMARIZATION_SERVICE_URL", "http://summarization:9002"
    )

    timeout_used = None

    class MockResponse:
        status_code = 200

        def raise_for_status(self):
            pass

        def json(self):
            return {"summary": "Summary"}

    class MockClient:
        def __init__(self, timeout=None):
            nonlocal timeout_used
            timeout_used = timeout

        async def __aenter__(self):
            return self

        async def __aexit__(self, *args):
            pass

        async def post(self, url, json=None, **kwargs):
            return MockResponse()

    monkeypatch.setattr("routes.summarization.httpx.AsyncClient", MockClient)

    response = client.post("/api/summarize", json={"text": "Test"})

    assert response.status_code == 200
    # Verify the AsyncClient was created with timeout=120.0
    assert timeout_used == 120.0


def test_summarize_multiline_text(client, monkeypatch):
    """
    Test summarization with multiline text containing newlines.
    """
    monkeypatch.setattr(
        summarization_route, "SUMMARIZATION_SERVICE_URL", "http://summarization:9002"
    )

    multiline_text = """Line 1
Line 2
Line 3

Paragraph 2"""

    class MockResponse:
        status_code = 200

        def raise_for_status(self):
            pass

        def json(self):
            return {"summary": "Multiline summary"}

    class MockClient:
        async def __aenter__(self):
            return self

        async def __aexit__(self, *args):
            pass

        async def post(self, url, json=None, **kwargs):
            assert "\n" in json["text"]
            return MockResponse()

    monkeypatch.setattr("routes.summarization.httpx.AsyncClient", lambda timeout: MockClient())

    response = client.post("/api/summarize", json={"text": multiline_text})

    assert response.status_code == 200


def test_save_summary_success(client, monkeypatch):
    """
    Test successful saving of a summary when user is authenticated.
    """

    async def mock_user_dependency():
        return {"_id": "user123"}  # return a user

    monkeypatch.setattr(
        summarization_route,
        "get_current_user",
        mock_user_dependency,
    )

    # Mock MongoDB insert_one
    mock_insert = AsyncMock()
    mock_insert.inserted_id = "abc123"

    # Mock DB collection on app state
    client.app.state.summaries = AsyncMock()
    client.app.state.summaries.insert_one = AsyncMock(return_value=mock_insert)

    payload = {"summary": "Short summary", "original_text": "Full text here"}

    response = client.post("/api/summarize/save", json=payload)

    assert response.status_code == 200
    assert response.json() == {"status": "saved", "summary_id": "abc123"}

    client.app.state.summaries.insert_one.assert_awaited_once()


def test_save_summary_unauthorized(client, monkeypatch):
    """
    Test that unauthorized users cannot save summaries.
    """

    async def mock_none():
        return None

    monkeypatch.setattr(
        summarization_route,
        "get_current_user",
        mock_none,
    )

    response = client.post(
        "/api/summarize/save",
        json={"summary": "x", "original_text": "y"},
    )

    assert response.status_code == 401


def test_save_summary_missing_fields(client, monkeypatch):
    """
    Test that backend returns 400 if summary or original_text is missing.
    """

    async def mock_user_dependency():
        return {"_id": "user123"}

    monkeypatch.setattr(
        summarization_route,
        "get_current_user",
        mock_user_dependency,
    )

    response = client.post(
        "/api/summarize/save",
        json={"summary": "Only summary"},
    )

    assert response.status_code == 400
    assert "Missing summary or original_text" in response.json()["detail"]


def test_get_history_success(client, monkeypatch):
    """
    Test fetching summary history successfully.
    """

    mock_user = {"_id": "abc123"}

    async def mock_user_dependency():
        return mock_user

    monkeypatch.setattr(
        summarization_route,
        "get_current_user",
        mock_user_dependency,
    )

    # Mock DB finder
    mock_doc = {
        "_id": "xyz789",
        "userId": "abc123",
        "original_text": "Full text",
        "summary": "Short summary",
        "created_at": datetime.now(UTC),
    }

    async def mock_cursor():
        yield mock_doc

    mock_find = AsyncMock()
    mock_find.sort.return_value = mock_cursor()

    client.app.state.summaries = AsyncMock()
    client.app.state.summaries.find.return_value = mock_find

    response = client.get("/api/summarize/history")

    assert response.status_code == 200
    data = response.json()["history"]

    assert len(data) == 1
    assert data[0]["summary"] == "Short summary"
    assert data[0]["_id"] == "xyz789"  # converted to string


def test_get_history_unauthorized(client, monkeypatch):
    """
    Test history returns 401 if no authenticated user.
    """

    async def mock_none():
        return None

    monkeypatch.setattr(
        summarization_route,
        "get_current_user",
        mock_none,
    )

    response = client.get("/api/summarize/history")

    assert response.status_code == 401


def test_get_history_empty(client, monkeypatch):
    """
    Test empty history returns an empty array.
    """

    async def mock_user_dependency():
        return {"_id": "u1"}

    monkeypatch.setattr(
        summarization_route,
        "get_current_user",
        mock_user_dependency,
    )

    async def empty_cursor():
        if False:
            yield

    mock_find = AsyncMock()
    mock_find.sort.return_value = empty_cursor()

    client.app.state.summaries = AsyncMock()
    client.app.state.summaries.find.return_value = mock_find

    response = client.get("/api/summarize/history")

    assert response.status_code == 200
    assert response.json()["history"] == []
