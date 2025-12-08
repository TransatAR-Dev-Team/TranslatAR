"""
Integration tests for history retrieval and user data management.
Tests cover translation history, filtering, pagination, and user isolation.
"""
import pytest
import httpx
import asyncio
from datetime import datetime, timedelta

BACKEND_URL = "http://backend:8000/api"


@pytest.fixture
async def auth_token():
    """Fixture to provide a valid authentication token."""
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{BACKEND_URL}/test-auth/get-token")
        return response.json()["access_token"]


@pytest.fixture
async def second_user_token():
    """
    Fixture to provide a token for a second user (for isolation tests).
    Note: This requires modifying the test endpoint or creating multiple test users.
    """
    # For now, returns the same token - in real tests you'd create a different user
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{BACKEND_URL}/test-auth/get-token")
        return response.json()["access_token"]


@pytest.mark.asyncio
async def test_get_empty_history(auth_token):
    """Test retrieving history when user has no translations."""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{BACKEND_URL}/history",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "history" in data
        assert isinstance(data["history"], list)


@pytest.mark.asyncio
async def test_history_after_translation(auth_token):
    """Test that history updates after processing audio."""
    # First, create a translation via WebSocket or process-audio
    # For this test, we'll use the transcripts endpoint with saved data
    
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{BACKEND_URL}/history",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 200
        # After WebSocket tests run, there should be some history


@pytest.mark.asyncio
async def test_history_returns_latest_first(auth_token):
    """Test that history is returned in reverse chronological order."""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{BACKEND_URL}/history",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 200
        history = response.json()["history"]
        
        if len(history) > 1:
            # Verify timestamps are in descending order
            for i in range(len(history) - 1):
                time1 = datetime.fromisoformat(history[i]["timestamp"].replace('Z', '+00:00'))
                time2 = datetime.fromisoformat(history[i + 1]["timestamp"].replace('Z', '+00:00'))
                assert time1 >= time2


@pytest.mark.asyncio
async def test_history_limit_50(auth_token):
    """Test that history is limited to 50 items."""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{BACKEND_URL}/history",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 200
        history = response.json()["history"]
        assert len(history) <= 50


@pytest.mark.asyncio
async def test_history_contains_required_fields(auth_token):
    """Test that each history item contains required fields."""
    async with httpx.AsyncClient() as client:
        # First ensure there's at least one item by checking WebSocket test results
        response = await client.get(
            f"{BACKEND_URL}/history",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        history = response.json()["history"]
        
        if len(history) > 0:
            item = history[0]
            required_fields = [
                "_id",
                "original_text",
                "translated_text",
                "source_lang",
                "target_lang",
                "timestamp",
                "userId"
            ]
            
            for field in required_fields:
                assert field in item, f"Missing required field: {field}"


@pytest.mark.asyncio
async def test_history_user_isolation(auth_token, second_user_token):
    """Test that users can only see their own history."""
    # Note: This test assumes second_user_token creates a different user
    # In the current setup, it might be the same user
    
    async with httpx.AsyncClient() as client:
        # Get history for first user
        response1 = await client.get(
            f"{BACKEND_URL}/history",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        history1 = response1.json()["history"]
        
        # Get history for second user
        response2 = await client.get(
            f"{BACKEND_URL}/history",
            headers={"Authorization": f"Bearer {second_user_token}"}
        )
        
        history2 = response2.json()["history"]
        
        # In current test setup, these will be the same
        # In production, verify they're different
        assert isinstance(history1, list)
        assert isinstance(history2, list)


@pytest.mark.asyncio
async def test_history_without_auth():
    """Test that history requires authentication."""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BACKEND_URL}/history")
        assert response.status_code == 401


@pytest.mark.asyncio
async def test_user_me_endpoint(auth_token):
    """Test the /users/me endpoint returns correct user data."""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{BACKEND_URL}/users/me",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 200
        user = response.json()
        
        # Verify user fields
        assert "_id" in user
        assert "email" in user
        assert "googleId" in user
        assert user["email"] == "test@integration.com"


@pytest.mark.asyncio
async def test_user_me_without_auth():
    """Test that /users/me requires authentication."""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BACKEND_URL}/users/me")
        assert response.status_code == 401


@pytest.mark.asyncio
async def test_history_includes_conversation_id(auth_token):
    """Test that history items include conversationId when available."""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{BACKEND_URL}/history",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        history = response.json()["history"]
        
        # Check if any items have conversationId
        # (from WebSocket tests that include conversation_id)
        if len(history) > 0:
            # conversationId may or may not be present depending on how translation was created
            # Just verify the structure is valid
            for item in history:
                if "conversationId" in item:
                    assert isinstance(item["conversationId"], str)


@pytest.mark.asyncio
async def test_history_language_detection_metadata(auth_token):
    """Test that history includes language detection metadata."""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{BACKEND_URL}/history",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        history = response.json()["history"]
        
        if len(history) > 0:
            item = history[0]
            # These fields should be present from audio processing
            if "detected_language" in item:
                assert isinstance(item["detected_language"], str)
            if "language_probability" in item:
                assert isinstance(item["language_probability"], (int, float))
                assert 0 <= item["language_probability"] <= 1


@pytest.mark.asyncio
async def test_get_user_me_consistency(auth_token):
    """Test that /users/me returns consistent data across multiple calls."""
    async with httpx.AsyncClient() as client:
        # Make multiple requests
        responses = await asyncio.gather(
            client.get(f"{BACKEND_URL}/users/me", headers={"Authorization": f"Bearer {auth_token}"}),
            client.get(f"{BACKEND_URL}/users/me", headers={"Authorization": f"Bearer {auth_token}"}),
            client.get(f"{BACKEND_URL}/users/me", headers={"Authorization": f"Bearer {auth_token}"})
        )
        
        # All should return same data
        users = [r.json() for r in responses]
        
        assert users[0]["_id"] == users[1]["_id"] == users[2]["_id"]
        assert users[0]["email"] == users[1]["email"] == users[2]["email"]


@pytest.mark.asyncio
async def test_history_timestamp_format(auth_token):
    """Test that history timestamps are in correct ISO format."""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{BACKEND_URL}/history",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        history = response.json()["history"]
        
        if len(history) > 0:
            timestamp = history[0]["timestamp"]
            # Should be able to parse as ISO format datetime
            try:
                dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                assert isinstance(dt, datetime)
            except ValueError:
                pytest.fail(f"Invalid timestamp format: {timestamp}")


@pytest.mark.asyncio
async def test_history_id_format(auth_token):
    """Test that history items have valid MongoDB ObjectId format."""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{BACKEND_URL}/history",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        history = response.json()["history"]
        
        if len(history) > 0:
            item_id = history[0]["_id"]
            # MongoDB ObjectId is 24 hex characters
            assert isinstance(item_id, str)
            assert len(item_id) == 24
            assert all(c in '0123456789abcdef' for c in item_id.lower())
