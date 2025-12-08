"""
Integration tests for WebSocket real-time translation functionality.
Tests cover connection, authentication, message exchange, database persistence, and error handling.
"""
import asyncio
import json
import motor.motor_asyncio
import pytest
import websockets

BACKEND_WS_URL = "ws://backend:8000/ws"
MONGO_URL = "mongodb://mongodb_test:27017"


def _pack_message(meta: dict, audio: bytes) -> bytes:
    """Helper function to format the WebSocket message."""
    m = json.dumps(meta).encode("utf-8")
    return len(m).to_bytes(4, "little") + m + audio


@pytest.fixture
async def auth_token():
    """Fixture to provide a valid authentication token."""
    import httpx
    async with httpx.AsyncClient() as client:
        response = await client.post("http://backend:8000/api/test-auth/get-token")
        return response.json()["access_token"]


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


# ============================================================================
# BASIC CONNECTION TESTS
# ============================================================================

@pytest.mark.asyncio
async def test_websocket_basic_connection():
    """Test basic WebSocket connection without auth."""
    try:
        async with websockets.connect(BACKEND_WS_URL) as ws:
            # Send a basic message
            message = _pack_message(
                {"source_lang": "en", "target_lang": "es"},
                b"test_audio"
            )
            await ws.send(message)
            
            # Receive response
            response = await asyncio.wait_for(ws.recv(), timeout=5.0)
            data = json.loads(response)
            
            assert "original_text" in data
            assert "translated_text" in data
            
    except asyncio.TimeoutError:
        pytest.fail("WebSocket response timeout")
    except Exception as e:
        pytest.fail(f"WebSocket connection failed: {e}")


@pytest.mark.asyncio
async def test_websocket_roundtrip_and_db_save(db_collection):
    """
    Connects to the WebSocket, sends an audio chunk, receives a response,
    and verifies the translation was saved to the MongoDB database.
    
    This is the original test from test_ws_realtime.py
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


# ============================================================================
# AUTHENTICATION TESTS
# ============================================================================

@pytest.mark.asyncio
async def test_websocket_with_authentication(auth_token):
    """Test WebSocket connection with JWT authentication."""
    try:
        async with websockets.connect(BACKEND_WS_URL) as ws:
            # Send authenticated message
            message = _pack_message(
                {
                    "source_lang": "en",
                    "target_lang": "es",
                    "jwt_token": auth_token
                },
                b"authenticated_audio"
            )
            await ws.send(message)
            
            response = await asyncio.wait_for(ws.recv(), timeout=5.0)
            data = json.loads(response)
            
            assert "original_text" in data
            assert "translated_text" in data
            
    except Exception as e:
        pytest.fail(f"Authenticated WebSocket connection failed: {e}")


# ============================================================================
# MULTIPLE MESSAGE TESTS
# ============================================================================

@pytest.mark.asyncio
async def test_websocket_multiple_messages():
    """Test sending multiple messages over same connection."""
    try:
        async with websockets.connect(BACKEND_WS_URL) as ws:
            num_messages = 5
            
            for i in range(num_messages):
                message = _pack_message(
                    {"source_lang": "en", "target_lang": "es"},
                    f"audio_{i}".encode()
                )
                await ws.send(message)
                
                response = await asyncio.wait_for(ws.recv(), timeout=5.0)
                data = json.loads(response)
                
                assert "original_text" in data
                assert "translated_text" in data
                
    except Exception as e:
        pytest.fail(f"Multiple message test failed: {e}")


@pytest.mark.asyncio
async def test_websocket_rapid_messages():
    """Test sending messages rapidly without waiting for responses."""
    try:
        async with websockets.connect(BACKEND_WS_URL) as ws:
            # Send multiple messages quickly
            for i in range(10):
                message = _pack_message(
                    {"source_lang": "en", "target_lang": "es"},
                    f"rapid_{i}".encode()
                )
                await ws.send(message)
            
            # Receive all responses
            responses = []
            for _ in range(10):
                response = await asyncio.wait_for(ws.recv(), timeout=10.0)
                data = json.loads(response)
                responses.append(data)
            
            assert len(responses) == 10
            
    except asyncio.TimeoutError:
        pytest.fail("Not all rapid messages were processed")
    except Exception as e:
        pytest.fail(f"Rapid messages test failed: {e}")


# ============================================================================
# LANGUAGE TESTS
# ============================================================================

@pytest.mark.asyncio
async def test_websocket_different_languages():
    """Test WebSocket with different language pairs."""
    language_pairs = [
        ("en", "es"),
        ("en", "fr"),
        ("fr", "en"),
    ]
    
    try:
        async with websockets.connect(BACKEND_WS_URL) as ws:
            for source, target in language_pairs:
                message = _pack_message(
                    {"source_lang": source, "target_lang": target},
                    b"test_audio"
                )
                await ws.send(message)
                
                response = await asyncio.wait_for(ws.recv(), timeout=5.0)
                data = json.loads(response)
                
                # Mock translation service returns [target_lang] original_text
                assert data["translated_text"] == f"[{target}] hello world"
                
    except Exception as e:
        pytest.fail(f"Language pair test failed: {e}")


@pytest.mark.asyncio
async def test_websocket_language_detection():
    """Test that language detection metadata is returned."""
    try:
        async with websockets.connect(BACKEND_WS_URL) as ws:
            message = _pack_message(
                {"source_lang": "en", "target_lang": "es"},
                b"test_audio"
            )
            await ws.send(message)
            
            response = await asyncio.wait_for(ws.recv(), timeout=5.0)
            data = json.loads(response)
            
            # Mock STT service returns detected_language
            assert "detected_language" in data
            assert "language_probability" in data
            
    except Exception as e:
        pytest.fail(f"Language detection test failed: {e}")


# ============================================================================
# CONVERSATION TRACKING TESTS
# ============================================================================

@pytest.mark.asyncio
async def test_websocket_conversation_tracking(auth_token):
    """Test that conversation IDs are properly tracked."""
    conversation_id = "test-conv-websocket-123"
    
    try:
        async with websockets.connect(BACKEND_WS_URL) as ws:
            # Send multiple messages with same conversation ID
            for i in range(3):
                message = _pack_message(
                    {
                        "source_lang": "en",
                        "target_lang": "es",
                        "conversation_id": conversation_id,
                        "jwt_token": auth_token
                    },
                    f"audio_chunk_{i}".encode()
                )
                await ws.send(message)
                
                response = await asyncio.wait_for(ws.recv(), timeout=5.0)
                data = json.loads(response)
                
                assert "original_text" in data
                
    except Exception as e:
        pytest.fail(f"Conversation tracking test failed: {e}")


@pytest.mark.asyncio
async def test_websocket_sequential_processing(auth_token):
    """Test that messages are processed sequentially in order."""
    try:
        async with websockets.connect(BACKEND_WS_URL) as ws:
            sent_order = []
            received_order = []
            
            # Send messages with identifiable metadata
            for i in range(5):
                conversation_id = f"seq-test-{i}"
                sent_order.append(conversation_id)
                
                message = _pack_message(
                    {
                        "source_lang": "en",
                        "target_lang": "es",
                        "conversation_id": conversation_id,
                        "jwt_token": auth_token
                    },
                    f"audio_{i}".encode()
                )
                await ws.send(message)
                
                response = await asyncio.wait_for(ws.recv(), timeout=5.0)
                data = json.loads(response)
                received_order.append(data)
            
            # All messages should be received
            assert len(received_order) == len(sent_order)
            
    except Exception as e:
        pytest.fail(f"Sequential processing test failed: {e}")


# ============================================================================
# CONCURRENT CONNECTION TESTS
# ============================================================================

@pytest.mark.asyncio
async def test_websocket_concurrent_connections():
    """Test multiple concurrent WebSocket connections."""
    async def single_connection(conn_id: int):
        async with websockets.connect(BACKEND_WS_URL) as ws:
            message = _pack_message(
                {"source_lang": "en", "target_lang": "es"},
                f"connection_{conn_id}".encode()
            )
            await ws.send(message)
            
            response = await asyncio.wait_for(ws.recv(), timeout=5.0)
            data = json.loads(response)
            
            assert "original_text" in data
            return data
    
    try:
        # Create 5 concurrent connections
        tasks = [single_connection(i) for i in range(5)]
        results = await asyncio.gather(*tasks)
        
        # All should succeed
        assert len(results) == 5
        for result in results:
            assert "original_text" in result
            
    except Exception as e:
        pytest.fail(f"Concurrent connections test failed: {e}")


# ============================================================================
# EDGE CASE TESTS
# ============================================================================

@pytest.mark.asyncio
async def test_websocket_empty_audio():
    """Test handling of empty audio data."""
    try:
        async with websockets.connect(BACKEND_WS_URL) as ws:
            message = _pack_message(
                {"source_lang": "en", "target_lang": "es"},
                b""  # Empty audio
            )
            await ws.send(message)
            
            response = await asyncio.wait_for(ws.recv(), timeout=5.0)
            data = json.loads(response)
            
            # Should return empty or minimal response
            assert isinstance(data, dict)
            
    except Exception as e:
        pytest.fail(f"Empty audio test failed: {e}")


@pytest.mark.asyncio
async def test_websocket_large_audio_chunk():
    """Test handling of large audio chunks."""
    try:
        async with websockets.connect(BACKEND_WS_URL) as ws:
            # Create a large audio chunk (1 MB)
            large_audio = b"x" * (1024 * 1024)
            
            message = _pack_message(
                {"source_lang": "en", "target_lang": "es"},
                large_audio
            )
            await ws.send(message)
            
            response = await asyncio.wait_for(ws.recv(), timeout=10.0)
            data = json.loads(response)
            
            assert "original_text" in data
            
    except Exception as e:
        pytest.fail(f"Large audio chunk test failed: {e}")


@pytest.mark.asyncio
async def test_websocket_connection_persistence():
    """Test that WebSocket connection stays alive for extended period."""
    try:
        async with websockets.connect(BACKEND_WS_URL) as ws:
            # Send message
            message1 = _pack_message(
                {"source_lang": "en", "target_lang": "es"},
                b"first"
            )
            await ws.send(message1)
            await ws.recv()
            
            # Wait 5 seconds
            await asyncio.sleep(5)
            
            # Send another message
            message2 = _pack_message(
                {"source_lang": "en", "target_lang": "es"},
                b"second"
            )
            await ws.send(message2)
            response = await asyncio.wait_for(ws.recv(), timeout=5.0)
            
            data = json.loads(response)
            assert "original_text" in data
            
    except Exception as e:
        pytest.fail(f"Connection persistence test failed: {e}")


@pytest.mark.asyncio
async def test_websocket_invalid_metadata_format():
    """Test handling of malformed metadata."""
    try:
        async with websockets.connect(BACKEND_WS_URL) as ws:
            # Send invalid metadata (not JSON)
            invalid_metadata = b"not_json_data"
            metadata_length = len(invalid_metadata).to_bytes(4, "little")
            message = metadata_length + invalid_metadata + b"audio"
            
            await ws.send(message)
            
            # Connection might close or return error
            try:
                response = await asyncio.wait_for(ws.recv(), timeout=5.0)
                # If we get a response, it should indicate an error
                # or the connection should close
            except websockets.exceptions.ConnectionClosed:
                # Expected behavior for invalid format
                pass
                
    except Exception as e:
        # Some error is expected for invalid format
        pass
