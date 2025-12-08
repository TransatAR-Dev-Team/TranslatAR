from datetime import datetime, timedelta

import httpx
import motor.motor_asyncio
import pytest # type: ignore[import-not-found]

BACKEND_URL = "http://backend:8000/api"
MONGO_URL = "mongodb://mongodb_test:27017"
DB_NAME = "translatar_db"
COLLECTION = "translations"


@pytest.fixture
async def transcripts_collection():
    """
    Provides a clean collection for testing.
    Uses unique markers to avoid conflicts with other tests.
    """
    client = None
    try:
        client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URL)
        collection = client[DB_NAME][COLLECTION]
        
        # Use unique test marker to avoid conflicts
        test_marker = f"test_transcripts_{datetime.utcnow().timestamp()}"
        
        yield collection, test_marker
    finally:
        if client:
            client.close()


@pytest.mark.asyncio
async def test_transcripts_returns_sorted_limited(transcripts_collection):
    collection, test_marker = transcripts_collection
    
    now = datetime.utcnow()
    docs = [
        {
            "test_marker": test_marker,
            "timestamp": now,
            "original_text": "latest",
            "translated_text": "[es] latest",
            "source_lang": "en",
            "target_lang": "es",
        },
        {
            "test_marker": test_marker,
            "timestamp": now - timedelta(minutes=1),
            "original_text": "older",
            "translated_text": "[es] older",
            "source_lang": "en",
            "target_lang": "es",
        },
        {
            "test_marker": test_marker,
            "timestamp": now - timedelta(minutes=2),
            "original_text": "oldest",
            "translated_text": "[es] oldest",
            "source_lang": "en",
            "target_lang": "es",
        },
    ]
    await collection.insert_many(docs)

    try:
        async with httpx.AsyncClient() as client:
            # Request enough items to ensure we get all our test data
            response = await client.post(f"{BACKEND_URL}/transcripts", json={"limit": 50})

        assert response.status_code == 200
        body = response.json()
        
        # Filter results to only our test data
        our_results = [doc for doc in body if doc.get("test_marker") == test_marker]
        
        # Should have all 3 of our documents
        assert len(our_results) == 3
        
        # Verify they're sorted by timestamp (newest first)
        assert our_results[0]["original_text"] == "latest"
        assert our_results[1]["original_text"] == "older"
        assert our_results[2]["original_text"] == "oldest"
        
        assert all(isinstance(doc["_id"], str) for doc in our_results)
    finally:
        # Clean up test data
        await collection.delete_many({"test_marker": test_marker})


@pytest.mark.asyncio
async def test_transcripts_applies_filters(transcripts_collection):
    collection, test_marker = transcripts_collection
    
    now = datetime.utcnow()
    docs = [
        {
            "test_marker": test_marker,
            "timestamp": now,
            "original_text": "alice-new",
            "userId": "alice",
            "source_lang": "en",
            "target_lang": "es",
        },
        {
            "test_marker": test_marker,
            "timestamp": now - timedelta(days=1),
            "original_text": "alice-old",
            "userId": "alice",
            "source_lang": "en",
            "target_lang": "es",
        },
        {
            "test_marker": test_marker,
            "timestamp": now - timedelta(hours=1),
            "original_text": "bob-new",
            "userId": "bob",
            "source_lang": "en",
            "target_lang": "es",
        },
    ]
    await collection.insert_many(docs)

    try:
        payload = {
            "limit": 50,
            "since": (now - timedelta(hours=12)).isoformat(),
            "user_id": "alice",
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(f"{BACKEND_URL}/transcripts", json=payload)

        assert response.status_code == 200
        body = response.json()
        
        # Filter to our test data only
        our_results = [doc for doc in body if doc.get("test_marker") == test_marker]
        
        # Should only get alice-new (within time range and matching user_id)
        assert len(our_results) == 1
        assert our_results[0]["original_text"] == "alice-new"
        assert our_results[0]["userId"] == "alice"
    finally:
        # Clean up test data
        await collection.delete_many({"test_marker": test_marker})


@pytest.mark.asyncio
async def test_transcripts_limit_validation(transcripts_collection):
    """Test that the transcripts endpoint properly limits results."""
    collection, test_marker = transcripts_collection
    
    # Insert 10 test documents
    now = datetime.utcnow()
    docs = [
        {
            "test_marker": test_marker,
            "timestamp": now - timedelta(minutes=i),
            "original_text": f"text_{i}",
            "translated_text": f"[es] text_{i}",
            "source_lang": "en",
            "target_lang": "es",
        }
        for i in range(10)
    ]
    await collection.insert_many(docs)

    try:
        # Request only 5 items
        async with httpx.AsyncClient() as client:
            response = await client.post(f"{BACKEND_URL}/transcripts", json={"limit": 5})

        assert response.status_code == 200
        body = response.json()
        
        # Total results should respect the limit (may include other test data)
        assert len(body) <= 5
        
    finally:
        # Clean up test data
        await collection.delete_many({"test_marker": test_marker})