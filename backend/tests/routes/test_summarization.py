from datetime import UTC, datetime
from unittest.mock import AsyncMock

import httpx
import pytest
from fastapi.testclient import TestClient

from main import app
from routes import summarization as summarization_route


class MockCursor:
    def __init__(self, docs):
        self.docs = docs

    def sort(self, *args, **kwargs):
        # Optionally sort by created_at descending
        self.docs.sort(key=lambda x: x.get("created_at", datetime.min), reverse=True)
        return self

    def __aiter__(self):
        self._iter = iter(self.docs)
        return self

    async def __anext__(self):
        try:
            return next(self._iter)
        except StopIteration:
            raise StopAsyncIteration from None


# --- Fixtures ---


@pytest.fixture
def client() -> TestClient:
    """Provides a test client for the FastAPI application."""
    return TestClient(app)


@pytest.fixture
def mock_summarization_service(monkeypatch):
    """Mock the summarization service HTTP call."""
    class MockResponse:
        status_code = 200

        def raise_for_status(self):
            pass

        def json(self):
            return {"summary": "Test summary"}

    class MockClient:
        async def __aenter__(self):
            return self

        async def __aexit__(self, *args):
            pass

        async def post(self, url, json=None, **kwargs):
            return MockResponse()

    monkeypatch.setattr(
        "routes.summarization.httpx.AsyncClient", lambda timeout=120.0: MockClient()
    )


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
            # Auto-downgrade may change the length for short texts
            assert json["length"] in ["short", "medium"]
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
    # Note: message may be present if auto-downgrade occurred


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

    # Use text with 400+ words to ensure it's long enough for "long" summary
    long_text = "word " * 400
    response = client.post(
        "/api/summarize",
        json={"text": long_text, "length": "long"},
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
            raise httpx.ConnectError("Service unavailable")

    monkeypatch.setattr("routes.summarization.httpx.AsyncClient", lambda timeout: MockClient())

    response = client.post("/api/summarize", json={"text": "Test text"})

    assert response.status_code == 503
    assert "unavailable" in response.json()["detail"]


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
            # Auto-downgrade will convert invalid_value to a valid length based on text size
            # Short text (5 words) will downgrade to "short"
            assert json["length"] == "short"
            return MockResponse()

    monkeypatch.setattr("routes.summarization.httpx.AsyncClient", lambda timeout: MockClient())

    response = client.post(
        "/api/summarize",
        json={"text": "Test text with few words", "length": "invalid_value"},
    )

    # The endpoint auto-downgrades invalid values to appropriate length based on text size
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


def test_save_summary_success(client):
    """Test successful saving of a summary when user is authenticated."""

    async def mock_user_dependency():
        return {"_id": "user123"}

    client.app.dependency_overrides[summarization_route.get_current_user] = mock_user_dependency

    mock_insert = AsyncMock()
    mock_insert.inserted_id = "abc123"

    client.app.state.summaries = AsyncMock()
    client.app.state.summaries.insert_one = AsyncMock(return_value=mock_insert)

    payload = {"summary": "Short summary", "original_text": "Full text here"}

    response = client.post("/api/summarize/save", json=payload)
    assert response.status_code == 200
    assert response.json() == {"status": "saved", "summary_id": "abc123"}

    client.app.state.summaries.insert_one.assert_awaited_once()

    client.app.dependency_overrides = {}


def test_save_summary_unauthorized(client):
    """Test that unauthorized users cannot save summaries."""

    async def mock_none():
        return None

    client.app.dependency_overrides[summarization_route.get_current_user] = mock_none

    response = client.post(
        "/api/summarize/save",
        json={"summary": "x", "original_text": "y"},
    )

    assert response.status_code == 401

    client.app.dependency_overrides = {}


def test_save_summary_missing_fields(client):
    """Test backend returns 422 if summary or original_text is missing."""

    async def mock_user_dependency():
        return {"_id": "user123"}

    client.app.dependency_overrides[summarization_route.get_current_user] = mock_user_dependency

    response = client.post("/api/summarize/save", json={"summary": "Only summary"})
    assert response.status_code == 422

    detail = response.json()["detail"]
    assert any(
        err["loc"] == ["body", "original_text"] and err["type"] == "missing" for err in detail
    )

    client.app.dependency_overrides = {}


def test_get_history_success(client):
    """Test fetching summary history successfully."""

    mock_user = {"_id": "abc123"}

    async def mock_user_dependency():
        return mock_user

    client.app.dependency_overrides[summarization_route.get_current_user] = mock_user_dependency

    mock_doc = {
        "_id": "xyz789",
        "userId": "abc123",
        "original_text": "Full text",
        "summary": "Short summary",
        "created_at": datetime.now(UTC),
    }

    client.app.state.summaries = type("obj", (), {})()
    client.app.state.summaries.find = lambda query: MockCursor([mock_doc])

    response = client.get("/api/summarize/history")
    assert response.status_code == 200

    data = response.json()["history"]
    assert len(data) == 1
    assert data[0]["summary"] == "Short summary"
    assert data[0]["_id"] == "xyz789"

    client.app.dependency_overrides = {}


def test_get_history_unauthorized(client):
    """Test history returns 401 if no authenticated user."""

    async def mock_none():
        return None

    client.app.dependency_overrides[summarization_route.get_current_user] = mock_none

    response = client.get("/api/summarize/history")
    assert response.status_code == 401

    client.app.dependency_overrides = {}


def test_get_history_empty(client):
    """Test empty history returns an empty array."""

    async def mock_user_dependency():
        return {"_id": "u1"}

    client.app.dependency_overrides[summarization_route.get_current_user] = mock_user_dependency

    client.app.state.summaries = type("obj", (), {})()
    client.app.state.summaries.find = lambda query: MockCursor([])
    response = client.get("/api/summarize/history")
    assert response.status_code == 200
    assert response.json()["history"] == []

    client.app.dependency_overrides = {}


# --- Auto-downgrade tests ---


def test_summarize_with_appropriate_length_no_downgrade(mock_summarization_service, client):
    """Test that no downgrade occurs when text length is appropriate."""
    # Text with 150 words (enough for medium, not enough for long)
    medium_text = "word " * 150
    resp = client.post(
        "/api/summarize", json={"text": medium_text, "length": "medium"}
    )
    assert resp.status_code == 200
    assert resp.json()["summary"] == "Test summary"
    assert resp.json().get("message") is None


def test_summarize_auto_downgrade_from_long_to_medium(mock_summarization_service, client):
    """Test auto-downgrade from long to medium when text is too short."""
    # Text with 150 words (enough for medium, not enough for long)
    medium_text = "word " * 150
    resp = client.post(
        "/api/summarize", json={"text": medium_text, "length": "long"}
    )
    assert resp.status_code == 200
    assert resp.json()["summary"] == "Test summary"
    assert resp.json()["message"] is not None
    assert "medium" in resp.json()["message"].lower()
    assert "long" in resp.json()["message"].lower()


def test_summarize_auto_downgrade_from_long_to_short(mock_summarization_service, client):
    """Test auto-downgrade from long to short when text is very short."""
    # Text with 50 words (only enough for short)
    short_text = "word " * 50
    resp = client.post(
        "/api/summarize", json={"text": short_text, "length": "long"}
    )
    assert resp.status_code == 200
    assert resp.json()["summary"] == "Test summary"
    assert resp.json()["message"] is not None
    assert "short" in resp.json()["message"].lower()
    assert "long" in resp.json()["message"].lower()


def test_summarize_auto_downgrade_from_medium_to_short(mock_summarization_service, client):
    """Test auto-downgrade from medium to short when text is too short."""
    # Text with 50 words (only enough for short)
    short_text = "word " * 50
    resp = client.post(
        "/api/summarize", json={"text": short_text, "length": "medium"}
    )
    assert resp.status_code == 200
    assert resp.json()["summary"] == "Test summary"
    assert resp.json()["message"] is not None
    assert "short" in resp.json()["message"].lower()
    assert "medium" in resp.json()["message"].lower()


def test_summarize_no_downgrade_for_long_text(mock_summarization_service, client):
    """Test that long text allows long summary without downgrade."""
    # Text with 400 words (enough for long)
    long_text = "word " * 400
    resp = client.post(
        "/api/summarize", json={"text": long_text, "length": "long"}
    )
    assert resp.status_code == 200
    assert resp.json()["summary"] == "Test summary"
    assert resp.json().get("message") is None
