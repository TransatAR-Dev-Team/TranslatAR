import json
import asyncio
import websockets


def pack(meta, audio: bytes):
    m = json.dumps(meta).encode("utf-8")
    return len(m).to_bytes(4, "little") + m + audio


async def _once():
    async with websockets.connect("ws://backend:8000/ws") as ws:
        await ws.send(pack({"source_lang": "en", "target_lang": "es"}, b"\x00" * 512))
        data = json.loads(await ws.recv())
        assert "translated_text" in data


def test_roundtrip(event_loop):
    event_loop.run_until_complete(_once())


