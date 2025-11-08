from types import SimpleNamespace

import pytest

import websocket as ws_mod


class StubWS:
    def __init__(self):
        self.sent = []
        # We will expose the mock collection to the test for assertions.
        self.mock_collection = self._MockCollection()
        self.app = SimpleNamespace(state=SimpleNamespace(db=self._get_mock_db()))

    class _MockCollection:
        def __init__(self):
            # This will store the document that was "inserted"
            self.inserted_doc = None

        async def insert_one(self, doc):
            # Capture the document instead of doing nothing
            self.inserted_doc = doc
            print(f"Mock DB captured: {self.inserted_doc}")

    def _get_mock_db(self):
        # This nested class structure keeps the mock self-contained.
        class MockDb:
            def __init__(self, collection_instance):
                self._collection = collection_instance

            def get_collection(self, name):
                # Always return the same instance of our mock collection
                return self._collection

        # Pass the pre-created collection instance to the mock DB
        return MockDb(self.mock_collection)

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
                return Resp({"transcription": "hello"})
            if url.endswith("/translate"):
                return Resp({"translated_text": "hola"})
            raise AssertionError(url)

    monkeypatch.setattr(ws_mod.httpx, "AsyncClient", lambda timeout=30.0: Client())
    ws = StubWS()
    await ws_mod.process_audio_chunk(ws, b"wav", "en", "es")

    assert ws.sent == [{"original_text": "hello", "translated_text": "hola"}]

    # Assert the database insertion was called correctly
    saved_doc = ws.mock_collection.inserted_doc
    assert saved_doc is not None
    assert saved_doc["original_text"] == "hello"
    assert saved_doc["translated_text"] == "hola"
    assert saved_doc["source_lang"] == "en"
    assert saved_doc["target_lang"] == "es"
    # Verify a timestamp was added
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

    monkeypatch.setattr(ws_mod.httpx, "AsyncClient", lambda timeout=3.0: BadClient())
    ws = StubWS()
    await ws_mod.process_audio_chunk(ws, b"x", "en", "es")
    assert ws.sent and "Error:" in ws.sent[0]["translated_text"]

    # Assert that nothing was saved to the DB on error
    assert ws.mock_collection.inserted_doc is None
