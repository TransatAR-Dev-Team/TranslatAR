import pytest
import httpx

BASE = "http://backend:8000/api"

@pytest.mark.asyncio
async def test_settings_round_trip_success():
    async with httpx.AsyncClient() as client:
        # 1) default values GET 
        r = await client.get(f"{BASE}/settings", timeout=10.0)
        assert r.status_code == 200
        assert "settings" in r.json()

        # 2) POST save
        payload = {
            "source_language": "ko",
            "target_language": "en",
            "chunk_duration_seconds": 4.0,
            "target_sample_rate": 48000,
            "silence_threshold": 0.01,
            "chunk_overlap_seconds": 0.5,
            "websocket_url": "ws://localhost:8000/ws"
        }
        r = await client.post(f"{BASE}/settings", json=payload, timeout=10.0)
        assert r.status_code == 200
        assert r.json()["settings"] == payload  # Check POST response reflects updates

        # 3) GET re-read: Check data persistence
        r = await client.get(f"{BASE}/settings", timeout=10.0)
        assert r.status_code == 200
        assert r.json()["settings"] == payload

@pytest.mark.asyncio
async def test_settings_invalid_type_returns_422():
    async with httpx.AsyncClient() as client:
        bad = {
            "source_language": "en",
            "target_language": "es",
            "chunk_duration_seconds": 8.0,
            "target_sample_rate": "not-an-int",  # Type error
            "silence_threshold": 0.01,
            "chunk_overlap_seconds": 0.5,
            "websocket_url": "ws://localhost:8000/ws"
        }
        r = await client.post(f"{BASE}/settings", json=bad, timeout=10.0)
        assert r.status_code == 422