import pytest

import websocket as ws_mod


class StubWS:
    def __init__(self):
        self.sent = []

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
    await ws_mod.process_audio_chunk(ws, b"x", "en", "es")
    assert ws.sent and "Error:" in ws.sent[0]["translated_text"]
