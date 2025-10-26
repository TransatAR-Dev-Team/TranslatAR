import pytest
from unittest.mock import Mock, patch, AsyncMock
from fastapi.testclient import TestClient
import jwt
import time
import os

# Set test environment variables before importing the app
os.environ["DATABASE_URL"] = "mongodb://localhost:27017"
os.environ["JWT_SECRET"] = "test_secret_key_for_jwt_signing"
os.environ["JWT_EXPIRE_MIN"] = "1440"
os.environ["GOOGLE_CLIENT_ID"] = "test_client_id"

from main import app
from database_client import DatabaseClient
from security import JWTManager


@pytest.fixture
def client():
    """Create a test client for the FastAPI app."""
    return TestClient(app)


@pytest.fixture
def mock_db_client():
    """Create a mock database client."""
    mock_db = AsyncMock(spec=DatabaseClient)
    app.state.db = mock_db
    return mock_db


def create_fake_google_id_token():
    """Create a fake Google ID Token for testing."""
    # Create a fake Google ID token with matching algorithm
    fake_header = {
        "alg": "HS256",
        "kid": "fake_key_id",
        "typ": "JWT"
    }
    
    fake_payload = {
        "sub": "123456789",  # Google user ID
        "email": "test@example.com",
        "name": "Test User",
        "picture": "https://example.com/photo.jpg",
        "iss": "https://accounts.google.com",
        "aud": "test_client_id",
        "exp": int(time.time()) + 3600,
        "iat": int(time.time())
    }
    
    # Note: This won't verify properly with JWKS, so we'll mock the verification
    return jwt.encode(fake_payload, "secret", algorithm="HS256", headers=fake_header)


def create_app_jwt():
    """Create an application JWT for testing."""
    return JWTManager.create_token(
        user_id="507f1f77bcf86cd799439011",
        email="test@example.com",
        name="Test User"
    )


@pytest.mark.asyncio
async def test_google_login_with_id_token(client, mock_db_client):
    """Test Google login with ID Token (client-side flow)."""
    # Mock the database response
    mock_user = {
        "_id": "507f1f77bcf86cd799439011",
        "google_id": "123456789",
        "email": "test@example.com",
        "name": "Test User",
        "picture": "https://example.com/photo.jpg"
    }
    mock_db_client.create_or_update_user.return_value = mock_user
    
    # Create fake Google ID token
    fake_id_token = create_fake_google_id_token()
    
    # Mock the Google ID Token verification
    with patch("security.GoogleIDTokenVerifier.verify_id_token") as mock_verify:
        # Mock the verification to return fake payload
        mock_verify.return_value = {
            "sub": "123456789",
            "email": "test@example.com",
            "name": "Test User",
            "picture": "https://example.com/photo.jpg",
            "aud": "test_client_id"
        }
        
        # Call the login endpoint
        response = client.post(
            "/api/auth/google/login",
            json={"idToken": fake_id_token}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Check new response format
        assert data["success"] is True
        assert "data" in data
        assert "token" in data["data"]
        assert "user" in data["data"]
        assert data["data"]["user"]["email"] == "test@example.com"
        assert data["data"]["user"]["name"] == "Test User"


def test_verify_token_valid(client):
    """Test JWT token verification with a valid token."""
    # Create a valid token using JWTManager
    token = create_app_jwt()
    
    # The verify endpoint now uses Authorization header
    response = client.get(
        "/api/auth/verify",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    
    # Check new response format
    assert data["success"] is True
    assert "data" in data
    assert data["data"]["valid"] is True
    assert "decoded" in data["data"]
    assert data["data"]["decoded"]["email"] == "test@example.com"


def test_verify_token_expired(client):
    """Test JWT token verification with an expired token."""
    # Create an expired token
    payload = {
        "user_id": "507f1f77bcf86cd799439011",
        "email": "test@example.com",
        "name": "Test User",
        "exp": time.time() - 3600,  # Expired 1 hour ago
        "iat": time.time() - 3600
    }
    token = jwt.encode(payload, "test_secret_key_for_jwt_signing", algorithm="HS256")
    
    response = client.get(
        "/api/auth/verify",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 401
    assert "expired" in response.json()["detail"].lower()


def test_verify_token_invalid(client):
    """Test JWT token verification with an invalid token."""
    response = client.get(
        "/api/auth/verify",
        headers={"Authorization": "Bearer invalid_token"}
    )
    
    assert response.status_code == 401
    assert "invalid" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_get_current_user_info(client, mock_db_client):
    """Test getting current user information with valid JWT."""
    # Create a valid token using JWTManager
    token = create_app_jwt()
    
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
        "/api/auth/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    
    # Check new response format
    assert data["success"] is True
    assert "data" in data
    assert data["data"]["email"] == "test@example.com"
    assert data["data"]["name"] == "Test User"
    assert "settings" in data["data"]


def test_get_current_user_no_token(client):
    """Test getting current user information without a token."""
    response = client.get("/api/auth/me")
    
    assert response.status_code == 401
    assert "Missing" in response.json()["detail"]


def test_get_current_user_invalid_token(client):
    """Test getting current user information with invalid token."""
    response = client.get(
        "/api/auth/me",
        headers={"Authorization": "Bearer invalid_token"}
    )
    
    assert response.status_code == 401

