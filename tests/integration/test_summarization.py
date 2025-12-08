"""
Integration tests for summarization and advice generation features.
Tests cover text summarization, summary saving, history retrieval, and advice generation.
"""
import pytest
import httpx
from datetime import datetime

BACKEND_URL = "http://backend:8000/api"


@pytest.fixture
async def auth_token():
    """Fixture to provide a valid authentication token."""
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{BACKEND_URL}/test-auth/get-token")
        return response.json()["access_token"]


async def check_summarization_service():
    """Check if summarization service is available."""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{BACKEND_URL}/summarize",
                json={"text": "test", "length": "short"},
                timeout=5.0
            )
            return response.status_code != 503
        except:
            return False


@pytest.mark.asyncio
async def test_summarize_short_text():
    """Test summarization with short length setting."""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BACKEND_URL}/summarize",
            json={
                "text": "This is a long piece of text that needs to be summarized. " * 10,
                "length": "short"
            },
            timeout=120.0
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert "summary" in data
        assert len(data["summary"]) > 0


@pytest.mark.asyncio
async def test_summarize_medium_text():
    """Test summarization with medium length setting."""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BACKEND_URL}/summarize",
            json={
                "text": "This is a long piece of text that needs to be summarized. " * 20,
                "length": "medium"
            },
            timeout=120.0
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "summary" in data


@pytest.mark.asyncio
async def test_summarize_long_text():
    """Test summarization with long length setting."""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BACKEND_URL}/summarize",
            json={
                "text": "This is a long piece of text that needs to be summarized. " * 30,
                "length": "long"
            },
            timeout=120.0
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "summary" in data


@pytest.mark.asyncio
async def test_summarize_empty_text():
    """Test that empty text is handled appropriately."""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BACKEND_URL}/summarize",
            json={
                "text": "",
                "length": "medium"
            },
            timeout=120.0
        )
        
        assert response.status_code == 200


@pytest.mark.asyncio
async def test_save_summary(auth_token):
    """Test saving a summary to the database."""
    async with httpx.AsyncClient() as client:
        # First generate a summary
        summarize_response = await client.post(
            f"{BACKEND_URL}/summarize",
            json={
                "text": "Test text for summarization.",
                "length": "short"
            },
            timeout=120.0
        )
        
        assert summarize_response.status_code == 200
        summary_text = summarize_response.json()["summary"]
        
        # Save the summary
        save_response = await client.post(
            f"{BACKEND_URL}/summarize/save",
            json={
                "summary": summary_text,
                "original_text": "Test text for summarization.",
                "conversationId": "test-conv-123"
            },
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert save_response.status_code == 200
        data = save_response.json()
        assert data["status"] == "saved"
        assert "summary_id" in data


@pytest.mark.asyncio
async def test_save_summary_without_auth():
    """Test that saving summary requires authentication."""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BACKEND_URL}/summarize/save",
            json={
                "summary": "Test summary",
                "original_text": "Test text"
            }
        )
        
        assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_summary_history(auth_token):
    """Test retrieving summary history."""
    async with httpx.AsyncClient() as client:
        # Save a summary first
        await client.post(
            f"{BACKEND_URL}/summarize/save",
            json={
                "summary": "Test summary for history",
                "original_text": "Original test text",
                "conversationId": "test-conv-456"
            },
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        # Retrieve history
        response = await client.get(
            f"{BACKEND_URL}/summarize/history",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "history" in data
        assert isinstance(data["history"], list)


@pytest.mark.asyncio
async def test_get_summary_history_by_conversation(auth_token):
    """Test retrieving summary history filtered by conversation ID."""
    conv_id = "test-conv-unique-789"
    
    async with httpx.AsyncClient() as client:
        # Save summaries with specific conversation ID
        for i in range(3):
            await client.post(
                f"{BACKEND_URL}/summarize/save",
                json={
                    "summary": f"Test summary {i}",
                    "original_text": f"Original text {i}",
                    "conversationId": conv_id
                },
                headers={"Authorization": f"Bearer {auth_token}"}
            )
        
        # Retrieve filtered history
        response = await client.get(
            f"{BACKEND_URL}/summarize/history?conversationId={conv_id}",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["history"]) >= 3
        
        # Verify all returned summaries have correct conversation ID
        for item in data["history"]:
            assert item["conversationId"] == conv_id


@pytest.mark.asyncio
async def test_advice_generation():
    """Test the advice generation endpoint."""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BACKEND_URL}/advice",
            json={"text": "I had a conversation in Spanish today."},
            timeout=120.0
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "advice" in data
        assert len(data["advice"]) > 0


@pytest.mark.asyncio
async def test_advice_with_empty_text():
    """Test advice generation with empty text."""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BACKEND_URL}/advice",
            json={"text": ""},
            timeout=120.0
        )
        
        # Should still return 200
        assert response.status_code == 200


@pytest.mark.asyncio
async def test_concurrent_summarizations():
    """Test that multiple concurrent summarization requests work correctly."""
    async with httpx.AsyncClient() as client:
        tasks = [
            client.post(
                f"{BACKEND_URL}/summarize",
                json={
                    "text": f"Test text {i} " * 20,
                    "length": "medium"
                },
                timeout=120.0
            )
            for i in range(3)
        ]
        
        responses = await asyncio.gather(*tasks, return_exceptions=True)
        
        for response in responses:
            assert not isinstance(response, Exception)
            assert response.status_code == 200
            assert "summary" in response.json()


@pytest.mark.asyncio
async def test_summarize_very_long_text():
    """Test summarization with very long text."""
    # Create a very long text (approximately 5000 words)
    long_text = "This is a test sentence with multiple words. " * 1000
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BACKEND_URL}/summarize",
            json={
                "text": long_text,
                "length": "medium"
            },
            timeout=300.0  # Longer timeout for large text
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "summary" in data
        # Summary should be significantly shorter than original
        assert len(data["summary"]) < len(long_text) / 2


@pytest.mark.asyncio
async def test_save_multiple_summaries_same_conversation(auth_token):
    """Test saving multiple summaries for the same conversation."""
    conv_id = "multi-summary-conv"
    
    async with httpx.AsyncClient() as client:
        summary_ids = []
        
        for i in range(3):
            response = await client.post(
                f"{BACKEND_URL}/summarize/save",
                json={
                    "summary": f"Summary version {i}",
                    "original_text": "Same original text",
                    "conversationId": conv_id
                },
                headers={"Authorization": f"Bearer {auth_token}"}
            )
            
            assert response.status_code == 200
            summary_ids.append(response.json()["summary_id"])
        
        # Verify all summaries are unique
        assert len(set(summary_ids)) == 3
        
        # Verify all can be retrieved
        history_response = await client.get(
            f"{BACKEND_URL}/summarize/history?conversationId={conv_id}",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert len(history_response.json()["history"]) >= 3


import asyncio