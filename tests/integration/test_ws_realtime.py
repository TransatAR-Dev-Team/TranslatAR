import asyncio
import json

import motor.motor_asyncio
import pytest
import websockets

BACKEND_WS_URL = "ws://backend:8000/ws"
MONGO_URL = "mongodb://mongodb:27017"


def _pack_message(meta: dict, audio: bytes) -> bytes:
    """Helper function to format the WebSocket message."""
    m = json.dumps(meta).encode("utf-8")
    return len(m).to_bytes(4, "little") + m + audio


@pytest.fixture
async def db_collection():
    """
    Provides a client connected to the test DB's 'translations'
    collection and handles cleanup.
    """
    client = None
    try:
        client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URL)
        db = client.translatar_db
        collection = db.translations
        # Clean up any old data before the test runs
        await collection.delete_many({"original_text": "hello world"})

        yield collection  # Provide the collection object to the test

    finally:
        # After the test, clean up the documents it created
        if client:
            await client.translatar_db.translations.delete_many(
                {"original_text": "hello world"}
            )
            client.close()


@pytest.mark.asyncio
async def test_websocket_roundtrip_and_db_save(db_collection):
    """
    Connects to the WebSocket, sends an audio chunk, receives a response,
    and verifies the translation was saved to the MongoDB database.
    """
    # 1. Connect to the WebSocket and send a message
    try:
        async with websockets.connect(BACKEND_WS_URL) as ws:
            # Use specific values that the mock services will return
            payload = _pack_message(
                {"source_lang": "en", "target_lang": "es"},
                audio=b"fake_audio_bytes"
            )
            await ws.send(payload)

            # 2. Receive and validate the response from the WebSocket
            response_data = await asyncio.wait_for(ws.recv(), timeout=5.0)
            response = json.loads(response_data)

            # The mock STT service returns "hello world"
            # The mock translation service returns "[target_lang] hello world"
            assert response["original_text"] == "hello world"
            assert response["translated_text"] == "[es] hello world"

    except Exception as e:
        pytest.fail(
            f"WebSocket communication failed. Is the backend service running? Error: {e}"
        )

    # 3. Verify the data was saved correctly in the database.
    # Add a small delay to ensure the background task in the backend has time to write to the DB.
    await asyncio.sleep(0.5)

    saved_doc = await db_collection.find_one({"original_text": "hello world"})

    assert saved_doc is not None, "Document was not found in the database!"
    assert saved_doc["translated_text"] == "[es] hello world"
    assert saved_doc["source_lang"] == "en"
    assert saved_doc["target_lang"] == "es"
    assert "timestamp" in saved_doc
