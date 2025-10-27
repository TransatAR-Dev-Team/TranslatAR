import json

from fastapi.testclient import TestClient

import websocket as ws_mod
from main import app


def _pack(meta: dict, audio: bytes) -> bytes:
    m = json.dumps(meta).encode("utf-8")
    return len(m).to_bytes(4, "little") + m + audio


def test_ws_route_parses_and_calls_processor(monkeypatch):
    called = {}

    async def fake_proc(ws, audio, src, tgt):
        called["audio"] = audio
        await ws.send_json({"original_text": "a", "translated_text": "b"})

    monkeypatch.setattr(ws_mod, "process_audio_chunk", fake_proc)

    with TestClient(app).websocket_connect("/ws") as ws:
        ws.send_bytes(_pack({"source_lang": "en", "target_lang": "es"}, b"123"))
        msg = ws.receive_json()

    assert called["audio"] == b"123"
    assert msg == {"original_text": "a", "translated_text": "b"}
