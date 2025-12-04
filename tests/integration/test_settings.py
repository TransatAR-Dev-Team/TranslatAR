import pytest
import httpx

BASE = "http://backend:8000/api" # This base URL is now correct for all API calls

@pytest.fixture(scope="module")
async def auth_headers():
    """
    Fixture to get a valid JWT token from the test-only endpoint.
    """
    # Use a separate client for the auth call since it's at a different base path
    async with httpx.AsyncClient(base_url="http://backend:8000") as client:
        # --- FIX: Update the URL to the correct, prefixed path ---
        response = await client.post("/api/test-auth/get-token")
        response.raise_for_status()
        token = response.json()["access_token"]
        return {"Authorization": f"Bearer {token}"}

@pytest.mark.asyncio
async def test_settings_round_trip_success(auth_headers):
    async with httpx.AsyncClient() as client:
        # Now we can use the main BASE URL for API calls
        r = await client.get(f"{BASE}/settings", headers=auth_headers, timeout=10.0)
        assert r.status_code == 200
        assert "settings" in r.json()

        payload = {
            "source_language": "ko", "target_language": "en",
            "chunk_duration_seconds": 4.0, "target_sample_rate": 48000,
            "silence_threshold": 0.01, "chunk_overlap_seconds": 0.5,
            "websocket_url": "ws://localhost:8000/ws", "subtitles_enabled": False,
            "translation_enabled": False, "subtitle_font_size": 24, "subtitle_style": "bold",
        }
        r = await client.post(f"{BASE}/settings", json=payload, headers=auth_headers, timeout=10.0)
        assert r.status_code == 200
        assert r.json()["settings"] == payload

        r = await client.get(f"{BASE}/settings", headers=auth_headers, timeout=10.0)
        assert r.status_code == 200
        assert r.json()["settings"] == payload

@pytest.mark.asyncio
async def test_settings_invalid_type_returns_422(auth_headers):
    async with httpx.AsyncClient() as client:
        bad_payload = {
            "source_language": "en", "target_language": "es",
            "chunk_duration_seconds": 8.0, "target_sample_rate": "not-an-int",
            "silence_threshold": 0.01, "chunk_overlap_seconds": 0.5,
            "websocket_url": "ws://localhost:8000/ws", "subtitles_enabled": True,
            "translation_enabled": True, "subtitle_font_size": 18, "subtitle_style": "normal",
        }
        r = await client.post(f"{BASE}/settings", json=bad_payload, headers=auth_headers, timeout=10.0)
        assert r.status_code == 422
