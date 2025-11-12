import httpx
import pytest
from datetime import datetime, timedelta, timezone

BASE = "http://backend:8000/api"


@pytest.mark.asyncio
async def test_history_without_google_id_returns_empty():
    async with httpx.AsyncClient() as client:
        r = await client.post(f"{BASE}/history/", data={}, timeout=10.0)
        assert r.status_code == 200

        body = r.json()
        assert "history" in body
        assert body["history"] == []


@pytest.mark.asyncio
async def test_history_filters_by_google_id(translations_collection):
    now = datetime.now(timezone.utc)

    await translations_collection.insert_many(
        [
            {
                "conversation_id": "conv123",
                "googleId": "gid-123",
                "username": "tester",
                "original_text": "Hello world",
                "translated_text": "Hola mundo",
                "source_lang": "en",
                "target_lang": "es",
                "timestamp": now,
            },
            {
                "conversation_id": "conv456",
                "googleId": "gid-456",
                "username": "tester",
                "original_text": "Goodbye",
                "translated_text": "Adiós",
                "source_lang": "en",
                "target_lang": "es",
                "timestamp": now + timedelta(seconds=1),
            },
        ]
    )

    async with httpx.AsyncClient() as client:
        r = await client.post(
            f"{BASE}/history/",
            data={"googleId": "gid-123"},
            timeout=10.0,
        )
        assert r.status_code == 200

        body = r.json()
        assert "history" in body
        assert len(body["history"]) == 1

        item = body["history"][0]
        assert item["googleId"] == "gid-123"
        assert item["original_text"] == "Hello world"


@pytest.mark.asyncio
async def test_history_filters_by_conversation_id(translations_collection):
    now = datetime.now(timezone.utc)

    await translations_collection.insert_many(
        [
            {
                "conversation_id": "conv789",
                "googleId": "gid-789",
                "username": "tester",
                "original_text": "Yes",
                "translated_text": "Sí",
                "source_lang": "en",
                "target_lang": "es",
                "timestamp": now,
            },
            {
                "conversation_id": "conv789",
                "googleId": "gid-789",
                "username": "tester",
                "original_text": "ciao",
                "translated_text": "hi",
                "source_lang": "it",
                "target_lang": "en",
                "timestamp": now + timedelta(seconds=1),
            },
        ]
    )

    async with httpx.AsyncClient() as client:
        r = await client.post(
            f"{BASE}/history/",
            data={"googleId": "gid-789", "conversation_id": "conv789"},
            timeout=10.0,
        )
        assert r.status_code == 200

        body = r.json()
        assert "history" in body
        assert len(body["history"]) == 2
        assert all(item["conversation_id"] == "conv789" for item in body["history"])