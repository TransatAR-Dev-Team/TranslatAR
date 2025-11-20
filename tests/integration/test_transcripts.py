from datetime import datetime, timedelta

import httpx
import motor.motor_asyncio
import pytest # type: ignore[import-not-found]

BACKEND_URL = "http://backend:8000/api"
MONGO_URL = "mongodb://mongodb_test:27017"
DB_NAME = "translatar_db"
COLLECTION = "translations"
MARKER = {"test_marker": "integration_transcripts"}


@pytest.fixture
async def transcripts_collection():
    client = None
    try:
        client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URL)
        collection = client[DB_NAME][COLLECTION]
        await collection.delete_many(MARKER)
        yield collection
    finally:
        if client:
            await client[DB_NAME][COLLECTION].delete_many(MARKER)
            client.close()


@pytest.mark.asyncio
async def test_transcripts_returns_sorted_limited(transcripts_collection):
    now = datetime.utcnow()
    docs = [
        {
            **MARKER,
            "timestamp": now,
            "original_text": "latest",
            "translated_text": "[es] latest",
        },
        {
            **MARKER,
            "timestamp": now - timedelta(minutes=1),
            "original_text": "older",
            "translated_text": "[es] older",
        },
        {
            **MARKER,
            "timestamp": now - timedelta(minutes=2),
            "original_text": "oldest",
            "translated_text": "[es] oldest",
        },
    ]
    await transcripts_collection.insert_many(docs)

    async with httpx.AsyncClient() as client:
        response = await client.post(f"{BACKEND_URL}/transcripts", json={"limit": 2})

    assert response.status_code == 200
    body = response.json()
    assert [doc["original_text"] for doc in body] == ["latest", "older"]
    assert all(isinstance(doc["_id"], str) for doc in body)


@pytest.mark.asyncio
async def test_transcripts_applies_filters(transcripts_collection):
    now = datetime.utcnow()
    docs = [
        {
            **MARKER,
            "timestamp": now,
            "original_text": "alice-new",
            "userId": "alice",
        },
        {
            **MARKER,
            "timestamp": now - timedelta(days=1),
            "original_text": "alice-old",
            "userId": "alice",
        },
        {
            **MARKER,
            "timestamp": now - timedelta(hours=1),
            "original_text": "bob-new",
            "userId": "bob",
        },
    ]
    await transcripts_collection.insert_many(docs)

    payload = {
        "limit": 50,
        "since": (now - timedelta(hours=12)).isoformat(),
        "user_id": "alice",
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(f"{BACKEND_URL}/transcripts", json=payload)

    assert response.status_code == 200
    body = response.json()
    assert len(body) == 1
    assert body[0]["original_text"] == "alice-new"
    assert body[0]["userId"] == "alice"

