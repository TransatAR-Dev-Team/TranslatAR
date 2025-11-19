from datetime import datetime, UTC
from io import BytesIO

import pytest
import httpx
from bson import ObjectId
from fastapi.testclient import TestClient

from main import app
from routes import process_audio as process_audio_route
from security.auth import get_current_user


# --- Fixtures ---


@pytest.fixture
def client() -> TestClient:
    """Provides a test client for the FastAPI application."""
    return TestClient(app)


@pytest.fixture
def mock_user():
    """Provides a mock user document."""
    return {
        "_id": ObjectId(),
        "googleId": "test_google_id_123",
        "email": "testuser@example.com",
        "username": "testuser",
        "createdAt": datetime.now(UTC),
        "updatedAt": datetime.now(UTC),
    }


@pytest.fixture
def fake_translations_collection():
    """Provides an in-memory mock of the translations collection."""

    class _Fake:
        def __init__(self):
            self._docs = []

        async def insert_one(self, doc: dict):
            self._docs.append(doc)
            return type("Result", (), {"acknowledged": True})()

    return _Fake()


@pytest.fixture(autouse=True)
def override_db_dependency(monkeypatch, fake_translations_collection):
    """
    Intercepts database calls and provides our in-memory mock collection.
    """
    monkeypatch.setattr(
        app.state.db,
        "get_collection",
        lambda name: fake_translations_collection if name == "translations" else None,
    )
    yield


@pytest.fixture
def authenticated_client(mock_user):
    """Fixture that provides authentication override."""
    async def mock_get_current_user():
        return mock_user
    
    app.dependency_overrides[get_current_user] = mock_get_current_user
    yield
    app.dependency_overrides.clear()


# --- Helper to create mock audio file ---


def create_mock_audio_file():
    """Creates a mock audio file for upload."""
    audio_data = b"fake_audio_bytes_here"
    return ("test_audio.wav", BytesIO(audio_data), "audio/wav")


# --- Tests for POST /api/process-audio ---


def test_process_audio_success(
    client, authenticated_client, monkeypatch, mock_user, fake_translations_collection
):
    """
    Test successful audio processing with transcription and translation.
    """
    # Mock service URLs
    monkeypatch.setattr(process_audio_route, "STT_SERVICE_URL", "http://stt:9000")
    monkeypatch.setattr(
        process_audio_route, "TRANSLATION_SERVICE_URL", "http://translation:9001"
    )

    # Mock httpx.AsyncClient
    class MockSTTResponse:
        status_code = 200

        def raise_for_status(self):
            pass

        def json(self):
            return {"transcription": "Hello world"}

    class MockTranslationResponse:
        status_code = 200

        def raise_for_status(self):
            pass

        def json(self):
            return {"translated_text": "Hola mundo"}

    class MockClient:
        async def __aenter__(self):
            return self

        async def __aexit__(self, *args):
            pass

        async def post(self, url, files=None, json=None, **kwargs):
            if "transcribe" in url:
                return MockSTTResponse()
            elif "translate" in url:
                assert json["text"] == "Hello world"
                assert json["source_lang"] == "en"
                assert json["target_lang"] == "es"
                return MockTranslationResponse()

    monkeypatch.setattr("routes.process_audio.httpx.AsyncClient", lambda timeout: MockClient())

    # Make request
    audio_file = create_mock_audio_file()
    response = client.post(
        "/api/process-audio",
        files={"audio_file": audio_file},
        data={"source_lang": "en", "target_lang": "es"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["original_text"] == "Hello world"
    assert data["translated_text"] == "Hola mundo"

    # Verify database was updated
    assert len(fake_translations_collection._docs) == 1
    saved_doc = fake_translations_collection._docs[0]
    assert saved_doc["original_text"] == "Hello world"
    assert saved_doc["translated_text"] == "Hola mundo"
    assert saved_doc["userId"] == str(mock_user["_id"])


def test_process_audio_default_languages(
    client, authenticated_client, monkeypatch, mock_user, fake_translations_collection
):
    """
    Test that default languages (en -> es) are used when not specified.
    """
    monkeypatch.setattr(process_audio_route, "STT_SERVICE_URL", "http://stt:9000")
    monkeypatch.setattr(
        process_audio_route, "TRANSLATION_SERVICE_URL", "http://translation:9001"
    )

    class MockSTTResponse:
        status_code = 200

        def raise_for_status(self):
            pass

        def json(self):
            return {"transcription": "Test"}

    class MockTranslationResponse:
        status_code = 200

        def raise_for_status(self):
            pass

        def json(self):
            return {"translated_text": "Prueba"}

    class MockClient:
        async def __aenter__(self):
            return self

        async def __aexit__(self, *args):
            pass

        async def post(self, url, files=None, json=None, **kwargs):
            if "transcribe" in url:
                return MockSTTResponse()
            elif "translate" in url:
                # Verify default languages were used
                assert json["source_lang"] == "en"
                assert json["target_lang"] == "es"
                return MockTranslationResponse()

    monkeypatch.setattr("routes.process_audio.httpx.AsyncClient", lambda timeout: MockClient())

    audio_file = create_mock_audio_file()
    # Don't specify languages - should default to en->es
    response = client.post(
        "/api/process-audio",
        files={"audio_file": audio_file},
    )

    assert response.status_code == 200


def test_process_audio_various_language_pairs(
    client, authenticated_client, monkeypatch, mock_user, fake_translations_collection
):
    """
    Test audio processing with different language pairs.
    """
    monkeypatch.setattr(process_audio_route, "STT_SERVICE_URL", "http://stt:9000")
    monkeypatch.setattr(
        process_audio_route, "TRANSLATION_SERVICE_URL", "http://translation:9001"
    )

    captured_langs = {}

    class MockSTTResponse:
        status_code = 200

        def raise_for_status(self):
            pass

        def json(self):
            return {"transcription": "Test text"}

    class MockTranslationResponse:
        status_code = 200

        def raise_for_status(self):
            pass

        def json(self):
            return {"translated_text": "Translated"}

    class MockClient:
        async def __aenter__(self):
            return self

        async def __aexit__(self, *args):
            pass

        async def post(self, url, files=None, json=None, **kwargs):
            if "transcribe" in url:
                return MockSTTResponse()
            elif "translate" in url:
                captured_langs["source"] = json["source_lang"]
                captured_langs["target"] = json["target_lang"]
                return MockTranslationResponse()

    monkeypatch.setattr("routes.process_audio.httpx.AsyncClient", lambda timeout: MockClient())

    # Test Korean to Chinese
    audio_file = create_mock_audio_file()
    response = client.post(
        "/api/process-audio",
        files={"audio_file": audio_file},
        data={"source_lang": "ko", "target_lang": "zh"},
    )

    assert response.status_code == 200
    assert captured_langs["source"] == "ko"
    assert captured_langs["target"] == "zh"


def test_process_audio_missing_audio_file(client, authenticated_client, mock_user):
    """
    Test that the endpoint returns 422 when audio file is missing.
    """
    response = client.post(
        "/api/process-audio", data={"source_lang": "en", "target_lang": "es"}
    )

    assert response.status_code == 422


def test_process_audio_unauthorized(client):
    """
    Test that the endpoint returns 401 when not authenticated.
    """
    audio_file = create_mock_audio_file()
    response = client.post("/api/process-audio", files={"audio_file": audio_file})

    assert response.status_code == 401


def test_process_audio_stt_service_error(
    client, authenticated_client, monkeypatch, mock_user, fake_translations_collection
):
    """
    Test handling of errors from the STT service.
    """
    monkeypatch.setattr(process_audio_route, "STT_SERVICE_URL", "http://stt:9000")

    class MockClient:
        async def __aenter__(self):
            return self

        async def __aexit__(self, *args):
            pass

        async def post(self, url, files=None, **kwargs):
            raise httpx.HTTPError("STT service unavailable")

    monkeypatch.setattr("routes.process_audio.httpx.AsyncClient", lambda timeout: MockClient())

    audio_file = create_mock_audio_file()
    response = client.post("/api/process-audio", files={"audio_file": audio_file})

    assert response.status_code == 500
    assert "Error in STT service" in response.json()["detail"]


def test_process_audio_stt_returns_no_transcription(
    client, authenticated_client, monkeypatch, mock_user, fake_translations_collection
):
    """
    Test handling when STT service returns empty or no transcription.
    """
    monkeypatch.setattr(process_audio_route, "STT_SERVICE_URL", "http://stt:9000")

    class MockSTTResponse:
        status_code = 200

        def raise_for_status(self):
            pass

        def json(self):
            return {}  # No 'transcription' field

    class MockClient:
        async def __aenter__(self):
            return self

        async def __aexit__(self, *args):
            pass

        async def post(self, url, files=None, **kwargs):
            return MockSTTResponse()

    monkeypatch.setattr("routes.process_audio.httpx.AsyncClient", lambda timeout: MockClient())

    audio_file = create_mock_audio_file()
    response = client.post("/api/process-audio", files={"audio_file": audio_file})

    assert response.status_code == 500
    assert "Transcription failed" in response.json()["detail"]


def test_process_audio_translation_service_error(
    client, authenticated_client, monkeypatch, mock_user, fake_translations_collection
):
    """
    Test handling of errors from the translation service.
    """
    monkeypatch.setattr(process_audio_route, "STT_SERVICE_URL", "http://stt:9000")
    monkeypatch.setattr(
        process_audio_route, "TRANSLATION_SERVICE_URL", "http://translation:9001"
    )

    class MockSTTResponse:
        status_code = 200

        def raise_for_status(self):
            pass

        def json(self):
            return {"transcription": "Test"}

    class MockClient:
        async def __aenter__(self):
            return self

        async def __aexit__(self, *args):
            pass

        async def post(self, url, files=None, json=None, **kwargs):
            if "transcribe" in url:
                return MockSTTResponse()
            elif "translate" in url:
                raise httpx.HTTPError("Translation service unavailable")

    monkeypatch.setattr("routes.process_audio.httpx.AsyncClient", lambda timeout: MockClient())

    audio_file = create_mock_audio_file()
    response = client.post("/api/process-audio", files={"audio_file": audio_file})

    assert response.status_code == 500
    assert "Error in Translation service" in response.json()["detail"]


def test_process_audio_translation_returns_none(
    client, authenticated_client, monkeypatch, mock_user, fake_translations_collection
):
    """
    Test handling when translation service returns no translated text.
    """
    monkeypatch.setattr(process_audio_route, "STT_SERVICE_URL", "http://stt:9000")
    monkeypatch.setattr(
        process_audio_route, "TRANSLATION_SERVICE_URL", "http://translation:9001"
    )

    class MockSTTResponse:
        status_code = 200

        def raise_for_status(self):
            pass

        def json(self):
            return {"transcription": "Test"}

    class MockTranslationResponse:
        status_code = 200

        def raise_for_status(self):
            pass

        def json(self):
            return {}  # No 'translated_text' field

    class MockClient:
        async def __aenter__(self):
            return self

        async def __aexit__(self, *args):
            pass

        async def post(self, url, files=None, json=None, **kwargs):
            if "transcribe" in url:
                return MockSTTResponse()
            elif "translate" in url:
                return MockTranslationResponse()

    monkeypatch.setattr("routes.process_audio.httpx.AsyncClient", lambda timeout: MockClient())

    audio_file = create_mock_audio_file()
    response = client.post("/api/process-audio", files={"audio_file": audio_file})

    assert response.status_code == 500
    assert "Translation failed" in response.json()["detail"]


def test_process_audio_database_save_failure(
    client, authenticated_client, monkeypatch, mock_user, capsys
):
    """
    Test that the endpoint still returns successfully even if database save fails.
    (The code prints a warning but doesn't fail the request)
    """
    monkeypatch.setattr(process_audio_route, "STT_SERVICE_URL", "http://stt:9000")
    monkeypatch.setattr(
        process_audio_route, "TRANSLATION_SERVICE_URL", "http://translation:9001"
    )

    # Create a mock collection that fails on insert
    class FailingCollection:
        async def insert_one(self, doc):
            raise Exception("Database connection lost")

    monkeypatch.setattr(
        app.state.db, "get_collection", lambda name: FailingCollection()
    )

    class MockSTTResponse:
        status_code = 200

        def raise_for_status(self):
            pass

        def json(self):
            return {"transcription": "Test"}

    class MockTranslationResponse:
        status_code = 200

        def raise_for_status(self):
            pass

        def json(self):
            return {"translated_text": "Prueba"}

    class MockClient:
        async def __aenter__(self):
            return self

        async def __aexit__(self, *args):
            pass

        async def post(self, url, files=None, json=None, **kwargs):
            if "transcribe" in url:
                return MockSTTResponse()
            elif "translate" in url:
                return MockTranslationResponse()

    monkeypatch.setattr("routes.process_audio.httpx.AsyncClient", lambda timeout: MockClient())

    audio_file = create_mock_audio_file()
    response = client.post("/api/process-audio", files={"audio_file": audio_file})

    # The endpoint should still return 200 despite database failure
    assert response.status_code == 200
    assert response.json()["original_text"] == "Test"
    assert response.json()["translated_text"] == "Prueba"


def test_process_audio_preserves_filename(
    client, authenticated_client, monkeypatch, mock_user, fake_translations_collection
):
    """
    Test that the audio filename is preserved when forwarding to STT service.
    """
    monkeypatch.setattr(process_audio_route, "STT_SERVICE_URL", "http://stt:9000")
    monkeypatch.setattr(
        process_audio_route, "TRANSLATION_SERVICE_URL", "http://translation:9001"
    )

    captured_filename = None

    class MockSTTResponse:
        status_code = 200

        def raise_for_status(self):
            pass

        def json(self):
            return {"transcription": "Test"}

    class MockTranslationResponse:
        status_code = 200

        def raise_for_status(self):
            pass

        def json(self):
            return {"translated_text": "Prueba"}

    class MockClient:
        async def __aenter__(self):
            return self

        async def __aexit__(self, *args):
            pass

        async def post(self, url, files=None, json=None, **kwargs):
            nonlocal captured_filename
            if "transcribe" in url and files:
                captured_filename = files["audio_file"][0]
            if "transcribe" in url:
                return MockSTTResponse()
            elif "translate" in url:
                return MockTranslationResponse()

    monkeypatch.setattr("routes.process_audio.httpx.AsyncClient", lambda timeout: MockClient())

    # Create audio file with specific filename
    audio_data = b"fake_audio"
    custom_filename = "my_recording.wav"
    audio_file = (custom_filename, BytesIO(audio_data), "audio/wav")

    response = client.post("/api/process-audio", files={"audio_file": audio_file})

    assert response.status_code == 200
    assert captured_filename == custom_filename


def test_process_audio_timeout_60_seconds(
    client, authenticated_client, monkeypatch, mock_user, fake_translations_collection
):
    """
    Test that the AsyncClient uses a 60-second timeout.
    """
    monkeypatch.setattr(process_audio_route, "STT_SERVICE_URL", "http://stt:9000")
    monkeypatch.setattr(
        process_audio_route, "TRANSLATION_SERVICE_URL", "http://translation:9001"
    )

    timeout_used = None

    class MockSTTResponse:
        status_code = 200

        def raise_for_status(self):
            pass

        def json(self):
            return {"transcription": "Test"}

    class MockTranslationResponse:
        status_code = 200

        def raise_for_status(self):
            pass

        def json(self):
            return {"translated_text": "Prueba"}

    class MockClient:
        def __init__(self, timeout=None):
            nonlocal timeout_used
            timeout_used = timeout

        async def __aenter__(self):
            return self

        async def __aexit__(self, *args):
            pass

        async def post(self, url, files=None, json=None, **kwargs):
            if "transcribe" in url:
                return MockSTTResponse()
            elif "translate" in url:
                return MockTranslationResponse()

    monkeypatch.setattr("routes.process_audio.httpx.AsyncClient", MockClient)

    audio_file = create_mock_audio_file()
    response = client.post("/api/process-audio", files={"audio_file": audio_file})

    assert response.status_code == 200
    assert timeout_used == 60.0


def test_process_audio_timestamp_saved(
    client, authenticated_client, monkeypatch, mock_user, fake_translations_collection
):
    """
    Test that a timestamp is saved with the translation record.
    """
    monkeypatch.setattr(process_audio_route, "STT_SERVICE_URL", "http://stt:9000")
    monkeypatch.setattr(
        process_audio_route, "TRANSLATION_SERVICE_URL", "http://translation:9001"
    )

    class MockSTTResponse:
        status_code = 200

        def raise_for_status(self):
            pass

        def json(self):
            return {"transcription": "Test"}

    class MockTranslationResponse:
        status_code = 200

        def raise_for_status(self):
            pass

        def json(self):
            return {"translated_text": "Prueba"}

    class MockClient:
        async def __aenter__(self):
            return self

        async def __aexit__(self, *args):
            pass

        async def post(self, url, files=None, json=None, **kwargs):
            if "transcribe" in url:
                return MockSTTResponse()
            elif "translate" in url:
                return MockTranslationResponse()

    monkeypatch.setattr("routes.process_audio.httpx.AsyncClient", lambda timeout: MockClient())

    audio_file = create_mock_audio_file()
    before_time = datetime.now(UTC)
    response = client.post("/api/process-audio", files={"audio_file": audio_file})
    after_time = datetime.now(UTC)

    assert response.status_code == 200

    # Verify timestamp is present and reasonable
    saved_doc = fake_translations_collection._docs[0]
    assert "timestamp" in saved_doc
    assert isinstance(saved_doc["timestamp"], datetime)
    assert before_time <= saved_doc["timestamp"] <= after_time