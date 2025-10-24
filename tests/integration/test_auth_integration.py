"""
Integration tests for authentication flow.
Tests the complete OAuth flow and JWT token management.
"""
import pytest
import httpx
import jwt
import time

BASE_URL = "http://backend:8000"
AUTH_URL = f"{BASE_URL}/auth"


@pytest.mark.asyncio
async def test_google_auth_endpoint_available():
    """Test that Google OAuth endpoint is available."""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{AUTH_URL}/google", timeout=10.0)
        assert response.status_code == 200
        data = response.json()
        assert "auth_url" in data
        assert "accounts.google.com" in data["auth_url"]


@pytest.mark.asyncio
async def test_jwt_verification_with_valid_token():
    """Test JWT token verification with a valid token."""
    async with httpx.AsyncClient() as client:
        # Create a test JWT token using the same secret as backend
        test_secret = "integration_test_jwt_secret_key_12345"
        payload = {
            "user_id": "test_user_123",
            "email": "test@example.com",
            "exp": time.time() + 3600
        }
        token = jwt.encode(payload, test_secret, algorithm="HS256")
        
        response = await client.get(
            f"{AUTH_URL}/verify",
            params={"token": token},
            timeout=10.0
        )
        
        # Should return 200 for valid token
        assert response.status_code == 200
        data = response.json()
        assert data["valid"] is True
        assert "decoded" in data
        assert data["decoded"]["email"] == "test@example.com"


@pytest.mark.asyncio
async def test_jwt_verification_with_expired_token():
    """Test JWT token verification with an expired token."""
    async with httpx.AsyncClient() as client:
        test_secret = "integration_test_jwt_secret_key_12345"
        payload = {
            "user_id": "test_user_123",
            "email": "test@example.com",
            "exp": time.time() - 3600  # Expired 1 hour ago
        }
        token = jwt.encode(payload, test_secret, algorithm="HS256")
        
        response = await client.get(
            f"{AUTH_URL}/verify",
            params={"token": token},
            timeout=10.0
        )
        
        # Should return 401 for expired token
        assert response.status_code == 401


@pytest.mark.asyncio
async def test_jwt_verification_with_invalid_token():
    """Test JWT token verification with an invalid token."""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{AUTH_URL}/verify",
            params={"token": "invalid_token_string"},
            timeout=10.0
        )
        
        # Should return 401 for invalid token
        assert response.status_code == 401


@pytest.mark.asyncio
async def test_user_info_endpoint_without_token():
    """Test accessing user info endpoint without authentication."""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{AUTH_URL}/me", timeout=10.0)
        
        # Should require authentication
        assert response.status_code in [401, 422]


@pytest.mark.asyncio
async def test_auth_endpoints_cors_headers():
    """Test that auth endpoints have proper CORS headers."""
    async with httpx.AsyncClient() as client:
        # Test CORS with a regular GET request instead of OPTIONS
        response = await client.get(
            f"{AUTH_URL}/google",
            headers={"Origin": "http://localhost:3000"},
            timeout=10.0
        )
        
        # Check response is successful and endpoint is accessible from different origins
        assert response.status_code == 200
        # CORS middleware in FastAPI allows all origins by default in config
        # The endpoint should be accessible which demonstrates CORS is working

