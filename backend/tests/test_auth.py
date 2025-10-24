import pytest
from unittest.mock import Mock, patch, AsyncMock
from fastapi.testclient import TestClient
import jwt
import time
import os

# Set test environment variables before importing the app
os.environ["DATABASE_URL"] = "mongodb://localhost:27017"
os.environ["JWT_SECRET"] = "test_secret_key"
os.environ["GOOGLE_CLIENT_ID"] = "test_client_id"
os.environ["GOOGLE_CLIENT_SECRET"] = "test_client_secret"
os.environ["GOOGLE_REDIRECT_URI"] = "http://localhost:8000/auth/google/callback"

from main import app
from database_client import DatabaseClient


@pytest.fixture
def client():
    """Create a test client for the FastAPI app."""
    return TestClient(app)


@pytest.fixture
def mock_db_client():
    """Create a mock database client."""
    mock_db = Mock(spec=DatabaseClient)
    app.state.db = mock_db
    return mock_db


def test_google_login_endpoint(client):
    """Test that the Google login endpoint returns an auth URL."""
    response = client.get("/auth/google")
    
    assert response.status_code == 200
    data = response.json()
    assert "auth_url" in data
    assert "accounts.google.com" in data["auth_url"]
    assert "client_id=test_client_id" in data["auth_url"]


@pytest.mark.asyncio
async def test_google_callback_success(client, mock_db_client):
    """Test successful Google OAuth callback."""
    # Mock the database response
    mock_user = {
        "_id": "507f1f77bcf86cd799439011",
        "google_id": "123456789",
        "email": "test@example.com",
        "name": "Test User"
    }
    mock_db_client.create_or_update_user.return_value = mock_user
    
    # Mock the Google API responses
    mock_token_response = {
        "access_token": "mock_access_token",
        "token_type": "Bearer"
    }
    
    mock_user_info = {
        "id": "123456789",
        "email": "test@example.com",
        "name": "Test User",
        "picture": "https://example.com/photo.jpg"
    }
    
    with patch("httpx.AsyncClient") as mock_client:
        mock_instance = AsyncMock()
        mock_client.return_value.__aenter__.return_value = mock_instance
        
        # Mock token exchange
        mock_token_resp = Mock()
        mock_token_resp.json = Mock(return_value=mock_token_response)
        mock_instance.post.return_value = mock_token_resp
        
        # Mock user info request
        mock_userinfo_resp = Mock()
        mock_userinfo_resp.json = Mock(return_value=mock_user_info)
        mock_instance.get.return_value = mock_userinfo_resp
        
        response = client.get("/auth/google/callback?code=test_auth_code")
        
        assert response.status_code == 200
        data = response.json()
        assert "jwt" in data
        assert "user" in data
        assert data["user"]["email"] == "test@example.com"


def test_verify_token_valid(client):
    """Test JWT token verification with a valid token."""
    # Create a valid token
    payload = {
        "user_id": "507f1f77bcf86cd799439011",
        "email": "test@example.com",
        "exp": time.time() + 3600
    }
    token = jwt.encode(payload, "test_secret_key", algorithm="HS256")
    
    response = client.get(f"/auth/verify?token={token}")
    
    assert response.status_code == 200
    data = response.json()
    assert data["valid"] is True
    assert "decoded" in data
    assert data["decoded"]["email"] == "test@example.com"


def test_verify_token_expired(client):
    """Test JWT token verification with an expired token."""
    # Create an expired token
    payload = {
        "user_id": "507f1f77bcf86cd799439011",
        "email": "test@example.com",
        "exp": time.time() - 3600  # Expired 1 hour ago
    }
    token = jwt.encode(payload, "test_secret_key", algorithm="HS256")
    
    response = client.get(f"/auth/verify?token={token}")
    
    assert response.status_code == 401
    assert "expired" in response.json()["detail"].lower()


def test_verify_token_invalid(client):
    """Test JWT token verification with an invalid token."""
    response = client.get("/auth/verify?token=invalid_token")
    
    assert response.status_code == 401
    assert "invalid" in response.json()["detail"].lower()


def test_get_current_user_info(client, mock_db_client):
    """Test getting current user information with valid JWT."""
    # Create a valid token
    payload = {
        "user_id": "507f1f77bcf86cd799439011",
        "email": "test@example.com",
        "name": "Test User",
        "exp": time.time() + 3600
    }
    token = jwt.encode(payload, "test_secret_key", algorithm="HS256")
    
    # Mock database response
    mock_user = {
        "_id": "507f1f77bcf86cd799439011",
        "google_id": "123456789",
        "email": "test@example.com",
        "name": "Test User",
        "picture": "https://example.com/photo.jpg",
        "settings": {
            "source_language": "en",
            "target_language": "es"
        }
    }
    mock_db_client.get_user_by_id.return_value = mock_user
    
    response = client.get(
        "/auth/me",
        params={"authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "test@example.com"
    assert data["name"] == "Test User"
    assert "settings" in data


def test_get_current_user_no_token(client):
    """Test getting current user information without a token."""
    response = client.get("/auth/me")
    
    assert response.status_code == 422  # Missing required parameter


def test_get_current_user_invalid_token(client):
    """Test getting current user information with invalid token."""
    response = client.get(
        "/auth/me",
        params={"authorization": "Bearer invalid_token"}
    )
    
    assert response.status_code == 401

