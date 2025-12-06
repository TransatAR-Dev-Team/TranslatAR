import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import WebSocketDisconnect
from fastapi.testclient import TestClient

from main import app
from routes import websocket as ws_mod

client = TestClient(app)


def _pack(meta: dict, audio: bytes) -> bytes:
    m = json.dumps(meta).encode("utf-8")
    return len(m).to_bytes(4, "little") + m + audio


@pytest.mark.asyncio
async def test_websocket_auth_failure(monkeypatch):
    """
    Test that connection closes with code 4001 if JWT is invalid.
    """
    monkeypatch.setattr("routes.websocket.verify_jwt_token", AsyncMock(return_value=None))

    with pytest.raises(WebSocketDisconnect) as exc:
        with client.websocket_connect("/ws") as ws:
            payload = _pack({"jwt_token": "bad_token"}, b"audio")
            ws.send_bytes(payload)
            ws.receive_json()

    assert exc.value.code == 4001


@pytest.mark.asyncio
async def test_websocket_loop_multiple_messages(monkeypatch):
    """
    Test the 'while True' loop processing multiple chunks.
    """
    monkeypatch.setattr("routes.websocket.verify_jwt_token", AsyncMock(return_value="user123"))

    mock_process = AsyncMock()
    monkeypatch.setattr("routes.websocket.process_audio_chunk", mock_process)

    with client.websocket_connect("/ws") as ws:
        # 1. First message (Auth + Audio)
        ws.send_bytes(_pack({"jwt_token": "valid", "conversation_id": "conv1"}, b"audio1"))

        # 2. Second message (Audio only, maintains context)
        ws.send_bytes(_pack({"source_lang": "en"}, b"audio2"))

        ws.close()

    assert mock_process.call_count == 2


@pytest.mark.asyncio
async def test_process_audio_chunk_db_save_failure(monkeypatch):
    """
    Test that DB save failure is logged but doesn't crash the connection.
    """

    class MockClient:
        async def __aenter__(self):
            return self

        async def __aexit__(self, *a):
            pass

        async def post(self, url, **kw):
            class Resp:
                def raise_for_status(self):
                    pass

                def json(self):
                    if "transcribe" in url:
                        return {"transcription": "Hi"}
                    return {"translated_text": "Hola"}

            return Resp()

    monkeypatch.setattr("routes.websocket.httpx.AsyncClient", lambda timeout=30.0: MockClient())

    class BrokenCollection:
        async def insert_one(self, doc):
            raise Exception("DB Disk Full")

    class BrokenDB:
        def get_collection(self, name):
            return BrokenCollection()

    class MockApp:
        state = type("State", (), {"db": BrokenDB()})()

    class MockWS:
        app = MockApp()

        async def send_json(self, data):
            self.sent_data = data

    ws = MockWS()

    await ws_mod.process_audio_chunk(ws, b"audio", "en", "es", "u1", "c1")

    # Assert success despite DB error (client still gets translation)
    assert ws.sent_data["translated_text"] == "Hola"


@pytest.mark.asyncio
async def test_process_audio_chunk_generic_exception(monkeypatch):
    """
    Test that generic exceptions inside processing are caught and sent as error JSON.
    """
    monkeypatch.setattr(
        "routes.websocket.httpx.AsyncClient", MagicMock(side_effect=ValueError("Random Crash"))
    )

    class MockWS:
        async def send_json(self, data):
            self.sent_data = data

    ws = MockWS()
    await ws_mod.process_audio_chunk(ws, b"audio", "en", "es", "u1", "c1")

    assert "Processing error" in ws.sent_data["translated_text"]
    assert "Random Crash" in ws.sent_data["translated_text"]


@pytest.mark.asyncio
async def test_websocket_unexpected_crash(monkeypatch):
    """
    Test the top-level 'except Exception' block in websocket_endpoint.
    """
    with patch("fastapi.WebSocket.receive_bytes", side_effect=ValueError("Socket Bomb")):
        with client.websocket_connect("/ws") as ws:
            with pytest.raises(WebSocketDisconnect):
                ws.receive_text()


@pytest.mark.asyncio
async def test_process_audio_chunk_empty_transcription(monkeypatch):
    """
    Test that if STT returns empty text (silence), we return early with empty strings
    and do NOT proceed to translation or database saving.
    """

    class MockClient:
        async def __aenter__(self):
            return self

        async def __aexit__(self, *a):
            pass

        async def post(self, url, **kw):
            class Resp:
                def raise_for_status(self):
                    pass

                def json(self):
                    # Simulate STT returning whitespace (silence)
                    if "transcribe" in url:
                        return {
                            "transcription": "   ",
                            "detected_language": "fr",
                            "language_probability": 0.8,
                        }
                    # Translate shouldn't be called, but just in case
                    return {"translated_text": "Should not happen"}

            return Resp()

    monkeypatch.setattr("routes.websocket.httpx.AsyncClient", lambda timeout=30.0: MockClient())

    class MockWS:
        # Minimal app state (db shouldn't be accessed in this path, but good for safety)
        app = type("App", (), {"state": type("State", (), {})()})()

        async def send_json(self, data):
            self.sent_data = data

    ws = MockWS()

    await ws_mod.process_audio_chunk(ws, b"silence_audio", "en", "es", "u1", "c1")

    # Verify we hit the early return block
    assert ws.sent_data["original_text"] == ""
    assert ws.sent_data["translated_text"] == ""
    assert ws.sent_data["detected_language"] == "fr"
    # Verify probability was passed through
    assert ws.sent_data["language_probability"] == 0.8
