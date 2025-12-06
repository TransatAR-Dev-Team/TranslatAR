from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient

from main import app, ml_models

client = TestClient(app)

# --- Helper Objects for Mocking Whisper ---


class MockInfo:
    def __init__(self, language="en", probability=0.95):
        self.language = language
        self.language_probability = probability


class MockSegment:
    def __init__(self, text, no_speech_prob=0.1):
        self.text = text
        self.no_speech_prob = no_speech_prob


# --- Tests ---


def test_health_check_model_loaded():
    """Test health check when model is loaded."""
    # Manually inject a mock model
    ml_models["whisper_model"] = "fake_model_object"

    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "model_loaded": True}

    # Cleanup
    ml_models.clear()


def test_health_check_model_not_loaded():
    """Test health check when model is missing."""
    ml_models.clear()

    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "model_loaded": False}


def test_transcribe_success():
    """
    Test the happy path: Model loaded, file uploaded, transcription returns text.
    """
    # 1. Setup the Mock Model
    mock_model = MagicMock()

    # define what .transcribe() returns (segments, info)
    segments = [MockSegment("Hello ", 0.0), MockSegment("world.", 0.0)]
    info = MockInfo(language="en", probability=0.99)

    mock_model.transcribe.return_value = (segments, info)

    # 2. Inject into global state
    ml_models["whisper_model"] = mock_model

    # 3. Create a dummy file
    files = {"audio_file": ("test.wav", b"fake audio data", "audio/wav")}

    # 4. Make Request
    response = client.post("/transcribe", files=files)

    # 5. Assertions
    assert response.status_code == 200
    data = response.json()
    assert data["transcription"] == "Hello world."
    assert data["detected_language"] == "en"
    assert data["language_probability"] == 0.99

    # Ensure transcribe was actually called
    mock_model.transcribe.assert_called_once()

    ml_models.clear()


def test_transcribe_filters_silence():
    """
    Test that segments with high 'no_speech_prob' are filtered out.
    """
    mock_model = MagicMock()
    segments = [
        MockSegment("Real speech. ", 0.1),
        MockSegment(" (silence) ", 0.9),  # Should be filtered out
    ]
    mock_model.transcribe.return_value = (segments, MockInfo())
    ml_models["whisper_model"] = mock_model

    files = {"audio_file": ("test.wav", b"data", "audio/wav")}
    response = client.post("/transcribe", files=files)

    assert response.status_code == 200
    # Should only contain the real speech
    assert response.json()["transcription"] == "Real speech."

    ml_models.clear()


def test_transcribe_model_not_loaded_returns_503():
    """
    Test that endpoint returns 503 Service Unavailable if model isn't in ml_models.
    """
    ml_models.clear()  # Ensure empty

    files = {"audio_file": ("test.wav", b"data", "audio/wav")}
    response = client.post("/transcribe", files=files)

    assert response.status_code == 503
    assert "not loaded" in response.json()["detail"]


def test_transcribe_internal_error_returns_500():
    """
    Test that if Whisper throws an exception, the API returns 500.
    """
    mock_model = MagicMock()
    # Force an exception
    mock_model.transcribe.side_effect = Exception("Whisper crashed")
    ml_models["whisper_model"] = mock_model

    files = {"audio_file": ("test.wav", b"data", "audio/wav")}
    response = client.post("/transcribe", files=files)

    assert response.status_code == 500
    assert "Whisper crashed" in response.json()["detail"]

    ml_models.clear()


# --- Lifespan (Startup/Shutdown) Tests ---


def test_lifespan_loads_model():
    """
    Test that the context manager correctly loads the model on startup
    and clears it on shutdown.
    """
    with patch("main.WhisperModel") as MockClass:
        # Mock the instance created
        MockClass.return_value = "MockedModelInstance"

        # Use TestClient as context manager to trigger startup/shutdown events
        with TestClient(app):
            # STARTUP should have happened
            assert "whisper_model" in ml_models
            assert ml_models["whisper_model"] == "MockedModelInstance"

        # SHUTDOWN should have happened
        assert "whisper_model" not in ml_models


def test_lifespan_handles_load_failure():
    """
    Test that if WhisperModel fails to load, the app logs it but doesn't crash
    (ml_models stays empty).
    """
    with patch("main.WhisperModel", side_effect=Exception("Disk full")):
        with TestClient(app):
            # Exception caught in main.py, logged as critical, model not loaded
            assert "whisper_model" not in ml_models
