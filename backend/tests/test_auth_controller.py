import pytest
import jwt
import time
from unittest.mock import Mock, patch, AsyncMock
from fastapi.testclient import TestClient
from fastapi import FastAPI
import httpx

# Import the auth controller
from auth_controller import router, OneTapRequest

# Create test app
app = FastAPI()
app.include_router(router)

# Mock database
class MockDB:
    def __init__(self):
        self.users = {}
        self.next_id = 1
    
    def create_or_update_user(self, user_info):
        # Find existing user by email
        for user_id, user in self.users.items():
            if user.get("email") == user_info.get("email"):
                # Update existing user
                self.users[user_id].update(user_info)
                return self.users[user_id]
        
        # Create new user
        user_id = str(self.next_id)
        self.next_id += 1
        user = {
            "_id": user_id,
            **user_info
        }
        self.users[user_id] = user
        return user
    
    def get_user_by_id(self, user_id):
        return self.users.get(user_id)

# Setup test database
test_db = MockDB()

# Set database in app state
@app.on_event("startup")
async def startup_event():
    app.state.db = test_db

# Manually set the database for testing
app.state.db = test_db

client = TestClient(app)

class TestGoogleLogin:
    """Test cases for Google OAuth login endpoint"""
    
    @patch.dict('os.environ', {
        'GOOGLE_CLIENT_ID': 'test_client_id',
        'GOOGLE_REDIRECT_URI': 'http://localhost:8000/auth/google/callback'
    })
    def test_google_login_success(self):
        """Test successful Google login URL generation"""
        response = client.get("/google")
        
        assert response.status_code == 200
        data = response.json()
        assert "auth_url" in data
        assert "test_client_id" in data["auth_url"]
        assert "http://localhost:8000/auth/google/callback" in data["auth_url"]
        assert "openid" in data["auth_url"]
        assert "email" in data["auth_url"]
        assert "profile" in data["auth_url"]
    
    @patch.dict('os.environ', {}, clear=True)
    def test_google_login_missing_config(self):
        """Test Google login with missing configuration"""
        response = client.get("/google")
        
        assert response.status_code == 500
        data = response.json()
        assert "Google OAuth not configured" in data["detail"]

class TestGoogleCallback:
    """Test cases for Google OAuth callback endpoint"""
    
    @patch.dict('os.environ', {
        'GOOGLE_CLIENT_ID': 'test_client_id',
        'GOOGLE_CLIENT_SECRET': 'test_client_secret',
        'GOOGLE_REDIRECT_URI': 'http://localhost:8000/auth/google/callback',
        'JWT_SECRET': 'test_jwt_secret'
    })
    @patch('httpx.AsyncClient')
    def test_google_callback_success(self, mock_httpx):
        """Test successful OAuth callback"""
        # Mock the token exchange response
        mock_token_response = Mock()
        mock_token_response.is_success = True
        mock_token_response.json.return_value = {
            "access_token": "test_access_token"
        }
        
        # Mock the user info response
        mock_user_response = Mock()
        mock_user_response.is_success = True
        mock_user_response.json.return_value = {
            "email": "test@example.com",
            "name": "Test User",
            "picture": "https://example.com/picture.jpg",
            "id": "google_user_123"
        }
        
        # Setup mock client
        mock_client = AsyncMock()
        mock_client.post.return_value = mock_token_response
        mock_client.get.return_value = mock_user_response
        mock_httpx.return_value.__aenter__.return_value = mock_client
        
        response = client.get("/google/callback?code=test_auth_code")
        
        assert response.status_code == 200
        data = response.json()
        assert "jwt" in data
        assert "user" in data
        assert data["user"]["email"] == "test@example.com"
        assert data["user"]["name"] == "Test User"
        
        # Verify JWT token
        token = data["jwt"]
        payload = jwt.decode(token, "test_jwt_secret", algorithms=["HS256"])
        assert payload["email"] == "test@example.com"
        assert payload["name"] == "Test User"
    
    def test_google_callback_missing_code(self):
        """Test OAuth callback with missing authorization code"""
        response = client.get("/google/callback")
        
        assert response.status_code == 400
        data = response.json()
        assert "No authorization code provided" in data["detail"]
    
    def test_google_callback_oauth_error(self):
        """Test OAuth callback with OAuth error"""
        response = client.get("/google/callback?error=access_denied")
        
        assert response.status_code == 400
        data = response.json()
        assert "OAuth error: access_denied" in data["detail"]

class TestGoogleOneTap:
    """Test cases for Google One-Tap authentication endpoint"""
    
    @patch.dict('os.environ', {
        'JWT_SECRET': 'test_jwt_secret'
    })
    @patch('httpx.AsyncClient')
    def test_google_one_tap_success(self, mock_httpx):
        """Test successful One-Tap authentication"""
        # Mock the token verification response
        mock_verify_response = Mock()
        mock_verify_response.is_success = True
        mock_verify_response.json.return_value = {
            "email": "test@example.com",
            "name": "Test User",
            "picture": "https://example.com/picture.jpg",
            "sub": "google_user_123"
        }
        
        # Setup mock client
        mock_client = AsyncMock()
        mock_client.get.return_value = mock_verify_response
        mock_httpx.return_value.__aenter__.return_value = mock_client
        
        request_data = {
            "credential": "test_google_id_token"
        }
        
        response = client.post("/google/one-tap", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        assert "jwt" in data
        assert "user" in data
        assert data["user"]["email"] == "test@example.com"
        assert data["user"]["name"] == "Test User"
        
        # Verify JWT token
        token = data["jwt"]
        payload = jwt.decode(token, "test_jwt_secret", algorithms=["HS256"])
        assert payload["email"] == "test@example.com"
        assert payload["name"] == "Test User"
    
    @patch('httpx.AsyncClient')
    def test_google_one_tap_invalid_token(self, mock_httpx):
        """Test One-Tap with invalid Google token"""
        # Mock failed token verification
        mock_verify_response = Mock()
        mock_verify_response.is_success = False
        
        # Setup mock client
        mock_client = AsyncMock()
        mock_client.get.return_value = mock_verify_response
        mock_httpx.return_value.__aenter__.return_value = mock_client
        
        request_data = {
            "credential": "invalid_token"
        }
        
        response = client.post("/google/one-tap", json=request_data)
        
        assert response.status_code == 400
        data = response.json()
        assert "Invalid Google token" in data["detail"]
    
    def test_google_one_tap_missing_credential(self):
        """Test One-Tap with missing credential"""
        request_data = {}
        
        response = client.post("/google/one-tap", json=request_data)
        
        assert response.status_code == 422  # Validation error

class TestTokenVerification:
    """Test cases for JWT token verification endpoint"""
    
    @patch.dict('os.environ', {
        'JWT_SECRET': 'test_jwt_secret'
    })
    def test_verify_token_success(self):
        """Test successful token verification"""
        # Create a valid JWT token
        payload = {
            "user_id": "1",
            "email": "test@example.com",
            "name": "Test User",
            "exp": time.time() + 3600  # 1 hour from now
        }
        token = jwt.encode(payload, "test_jwt_secret", algorithm="HS256")
        
        # Add user to test database
        test_db.users["1"] = {
            "_id": "1",
            "email": "test@example.com",
            "name": "Test User",
            "picture": "https://example.com/picture.jpg"
        }
        
        response = client.get(f"/verify?token={token}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["valid"] == True
        assert data["user"]["email"] == "test@example.com"
        assert data["user"]["name"] == "Test User"
    
    @patch.dict('os.environ', {
        'JWT_SECRET': 'test_jwt_secret'
    })
    def test_verify_token_expired(self):
        """Test verification of expired token"""
        # Create an expired JWT token
        payload = {
            "user_id": "1",
            "email": "test@example.com",
            "name": "Test User",
            "exp": time.time() - 3600  # 1 hour ago
        }
        token = jwt.encode(payload, "test_jwt_secret", algorithm="HS256")
        
        response = client.get(f"/verify?token={token}")
        
        assert response.status_code == 401
        data = response.json()
        assert "Token expired" in data["detail"]
    
    def test_verify_token_invalid(self):
        """Test verification of invalid token"""
        invalid_token = "invalid.jwt.token"
        
        response = client.get(f"/verify?token={invalid_token}")
        
        assert response.status_code == 401
        data = response.json()
        assert "Invalid token" in data["detail"]
    
    def test_verify_token_missing(self):
        """Test verification without token parameter"""
        response = client.get("/verify")
        
        assert response.status_code == 422  # Validation error

class TestDatabaseIntegration:
    """Test cases for database integration"""
    
    def test_user_creation_and_retrieval(self):
        """Test user creation and retrieval from database"""
        # Clear test database
        test_db.users.clear()
        test_db.next_id = 1
        
        # Test user creation
        user_info = {
            "email": "newuser@example.com",
            "name": "New User",
            "picture": "https://example.com/newuser.jpg",
            "sub": "google_user_456"
        }
        
        user = test_db.create_or_update_user(user_info)
        
        assert user["email"] == "newuser@example.com"
        assert user["name"] == "New User"
        assert user["_id"] == "1"
        
        # Test user retrieval
        retrieved_user = test_db.get_user_by_id("1")
        assert retrieved_user["email"] == "newuser@example.com"
        assert retrieved_user["name"] == "New User"
    
    def test_user_update(self):
        """Test updating existing user"""
        # Clear test database
        test_db.users.clear()
        test_db.next_id = 1
        
        # Create initial user
        initial_user_info = {
            "email": "updateuser@example.com",
            "name": "Original Name",
            "picture": "https://example.com/old.jpg",
            "sub": "google_user_789"
        }
        user = test_db.create_or_update_user(initial_user_info)
        user_id = user["_id"]
        
        # Update user
        updated_user_info = {
            "email": "updateuser@example.com",
            "name": "Updated Name",
            "picture": "https://example.com/new.jpg",
            "sub": "google_user_789"
        }
        updated_user = test_db.create_or_update_user(updated_user_info)
        
        assert updated_user["_id"] == user_id  # Same user ID
        assert updated_user["name"] == "Updated Name"  # Updated name
        assert updated_user["picture"] == "https://example.com/new.jpg"  # Updated picture
