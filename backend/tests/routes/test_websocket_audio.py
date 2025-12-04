import pytest
from types import SimpleNamespace
from main import app
from routes import websocket as ws_mod

# --- Mock Database Setup ---

class MockCollection:
    def __init__(self):
        self.inserted_doc = None
    async def insert_one(self, doc):
        self.inserted_doc = doc

class MockDb:
    def get_collection(self, name):
        return MockCollection()

class StubWS:
    def __init__(self):
        self.sent = []
        self.mock_collection = MockCollection()
        self.app = SimpleNamespace(
            state=SimpleNamespace(
                db=SimpleNamespace(
                    get_collection=lambda name: self.mock_collection
                )
            )
        )

    async def send_json(self, obj):
        self.sent.append(obj)


@pytest.mark.asyncio
async def test_process_audio_chunk_success(monkeypatch):
    class Resp:
        def __init__(self, d):
            self._d = d

        def raise_for_status(self):
            pass

        def json(self):
            return self._d

    class Client:
        async def __aenter__(self):
            return self

        async def __aexit__(self, *a):
            pass

        async def post(self, url, **kw):
            if url.endswith("/transcribe"):
                # Simulate STT service response with language detection
                return Resp({"transcription": "hello", "detected_language": "en", "language_probability": 0.9})
            if url.endswith("/translate"):
                return Resp({"translated_text": "hola"})
            raise AssertionError(url)

    monkeypatch.setattr(ws_mod.httpx, "AsyncClient", lambda timeout=30.0: Client())
    ws = StubWS()
    await ws_mod.process_audio_chunk(ws, b"wav", "en", "es", None, "dummy_convo_id")

    # Assert the response sent back to the client is correct
    assert len(ws.sent) == 1
    assert ws.sent[0]["original_text"] == "hello"
    assert ws.sent[0]["translated_text"] == "hola"
    assert ws.sent[0]["detected_language"] == "en"
    assert ws.sent[0]["language_probability"] == 0.9

    # Assert the database insertion was called correctly
    saved_doc = ws.mock_collection.inserted_doc
    assert saved_doc is not None
    assert saved_doc["original_text"] == "hello"
    assert saved_doc["translated_text"] == "hola"
    assert saved_doc["source_lang"] == "en" # effective_source_lang
    assert saved_doc["target_lang"] == "es"
    assert "timestamp" in saved_doc


@pytest.mark.asyncio
async def test_process_audio_chunk_stt_error(monkeypatch):
    class BadClient:
        async def __aenter__(self):
            return self

        async def __aexit__(self, *a):
            pass

        async def post(self, url, **kw):
            raise ws_mod.httpx.HTTPError("boom")

    monkeypatch.setattr(ws_mod.httpx, "AsyncClient", lambda timeout=30.0: BadClient())
    ws = StubWS()
    await ws_mod.process_audio_chunk(ws, b"x", "en", "es", None, "dummy_convo_id")
    assert ws.sent and "Error:" in ws.sent[0]["translated_text"]

    # Assert that nothing was saved to the DB on error
    assert ws.mock_collection.inserted_doc is None
