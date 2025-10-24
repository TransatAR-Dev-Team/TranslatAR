import pytest
import httpx
import jwt
import time
from unittest.mock import patch
from fastapi.testclient import TestClient
from fastapi import FastAPI

# Import the auth controller
from auth_controller import router

# Create test app
app = FastAPI()
app.include_router(router)

# Mock database for integration tests
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

class TestOAuthFlowIntegration:
    """Integration tests for complete OAuth flow"""
    
    @patch.dict('os.environ', {
        'GOOGLE_CLIENT_ID': 'test_client_id',
        'GOOGLE_CLIENT_SECRET': 'test_client_secret',
        'GOOGLE_REDIRECT_URI': 'http://localhost:8000/auth/google/callback',
        'JWT_SECRET': 'test_jwt_secret'
    })
    @patch('httpx.AsyncClient')
    def test_complete_oauth_flow(self, mock_httpx):
        """Test complete OAuth flow from login to token verification"""
        # Step 1: Get OAuth URL
        login_response = client.get("/google")
        assert login_response.status_code == 200
        auth_url = login_response.json()["auth_url"]
        assert "test_client_id" in auth_url
        assert "http://localhost:8000/auth/google/callback" in auth_url
        
        # Step 2: Mock OAuth callback
        mock_token_response = Mock()
        mock_token_response.is_success = True
        mock_token_response.json.return_value = {
            "access_token": "test_access_token"
        }
        
        mock_user_response = Mock()
        mock_user_response.is_success = True
        mock_user_response.json.return_value = {
            "email": "integration@example.com",
            "name": "Integration Test User",
            "picture": "https://example.com/integration.jpg",
            "id": "google_user_integration"
        }
        
        mock_client = Mock()
        mock_client.post.return_value = mock_token_response
        mock_client.get.return_value = mock_user_response
        mock_httpx.return_value.__aenter__.return_value = mock_client
        
        # Step 3: Handle OAuth callback
        callback_response = client.get("/google/callback?code=test_auth_code")
        assert callback_response.status_code == 200
        
        callback_data = callback_response.json()
        assert "jwt" in callback_data
        assert "user" in callback_data
        assert callback_data["user"]["email"] == "integration@example.com"
        
        # Step 4: Verify the JWT token
        jwt_token = callback_data["jwt"]
        verify_response = client.get(f"/verify?token={jwt_token}")
        assert verify_response.status_code == 200
        
        verify_data = verify_response.json()
        assert verify_data["valid"] == True
        assert verify_data["user"]["email"] == "integration@example.com"
        assert verify_data["user"]["name"] == "Integration Test User"
    
    @patch.dict('os.environ', {
        'JWT_SECRET': 'test_jwt_secret'
    })
    @patch('httpx.AsyncClient')
    def test_complete_one_tap_flow(self, mock_httpx):
        """Test complete One-Tap authentication flow"""
        # Mock Google token verification
        mock_verify_response = Mock()
        mock_verify_response.is_success = True
        mock_verify_response.json.return_value = {
            "email": "onetap@example.com",
            "name": "One-Tap User",
            "picture": "https://example.com/onetap.jpg",
            "sub": "google_user_onetap"
        }
        
        mock_client = Mock()
        mock_client.get.return_value = mock_verify_response
        mock_httpx.return_value.__aenter__.return_value = mock_client
        
        # Step 1: One-Tap authentication
        one_tap_request = {
            "credential": "test_google_id_token"
        }
        
        one_tap_response = client.post("/google/one-tap", json=one_tap_request)
        assert one_tap_response.status_code == 200
        
        one_tap_data = one_tap_response.json()
        assert "jwt" in one_tap_data
        assert "user" in one_tap_data
        assert one_tap_data["user"]["email"] == "onetap@example.com"
        
        # Step 2: Verify the JWT token
        jwt_token = one_tap_data["jwt"]
        verify_response = client.get(f"/verify?token={jwt_token}")
        assert verify_response.status_code == 200
        
        verify_data = verify_response.json()
        assert verify_data["valid"] == True
        assert verify_data["user"]["email"] == "onetap@example.com"
        assert verify_data["user"]["name"] == "One-Tap User"

class TestErrorHandlingIntegration:
    """Integration tests for error handling scenarios"""
    
    @patch.dict('os.environ', {
        'GOOGLE_CLIENT_ID': 'test_client_id',
        'GOOGLE_CLIENT_SECRET': 'test_client_secret',
        'GOOGLE_REDIRECT_URI': 'http://localhost:8000/auth/google/callback',
        'JWT_SECRET': 'test_jwt_secret'
    })
    @patch('httpx.AsyncClient')
    def test_oauth_flow_with_google_error(self, mock_httpx):
        """Test OAuth flow when Google returns an error"""
        # Mock failed token exchange
        mock_token_response = Mock()
        mock_token_response.is_success = False
        mock_token_response.status_code = 400
        
        mock_client = Mock()
        mock_client.post.return_value = mock_token_response
        mock_httpx.return_value.__aenter__.return_value = mock_client
        
        # OAuth callback should fail
        callback_response = client.get("/google/callback?code=invalid_code")
        assert callback_response.status_code == 400
        assert "Failed to exchange code for token" in callback_response.json()["detail"]
    
    @patch('httpx.AsyncClient')
    def test_one_tap_flow_with_invalid_token(self, mock_httpx):
        """Test One-Tap flow with invalid Google token"""
        # Mock failed token verification
        mock_verify_response = Mock()
        mock_verify_response.is_success = False
        
        mock_client = Mock()
        mock_client.get.return_value = mock_verify_response
        mock_httpx.return_value.__aenter__.return_value = mock_client
        
        one_tap_request = {
            "credential": "invalid_google_token"
        }
        
        one_tap_response = client.post("/google/one-tap", json=one_tap_request)
        assert one_tap_response.status_code == 400
        assert "Invalid Google token" in one_tap_response.json()["detail"]

class TestDatabaseIntegration:
    """Integration tests for database operations"""
    
    def test_user_persistence_across_requests(self):
        """Test that user data persists across multiple requests"""
        # Clear test database
        test_db.users.clear()
        test_db.next_id = 1
        
        # Create a user
        user_info = {
            "email": "persistence@example.com",
            "name": "Persistence User",
            "picture": "https://example.com/persistence.jpg",
            "sub": "google_user_persistence"
        }
        
        user = test_db.create_or_update_user(user_info)
        user_id = user["_id"]
        
        # Verify user exists
        retrieved_user = test_db.get_user_by_id(user_id)
        assert retrieved_user is not None
        assert retrieved_user["email"] == "persistence@example.com"
        
        # Update user
        updated_info = {
            "email": "persistence@example.com",
            "name": "Updated Persistence User",
            "picture": "https://example.com/updated.jpg",
            "sub": "google_user_persistence"
        }
        
        updated_user = test_db.create_or_update_user(updated_info)
        assert updated_user["_id"] == user_id  # Same user
        assert updated_user["name"] == "Updated Persistence User"
        
        # Verify update persisted
        final_user = test_db.get_user_by_id(user_id)
        assert final_user["name"] == "Updated Persistence User"
        assert final_user["picture"] == "https://example.com/updated.jpg"

class TestJWTTokenIntegration:
    """Integration tests for JWT token handling"""
    
    @patch.dict('os.environ', {
        'JWT_SECRET': 'test_jwt_secret'
    })
    def test_jwt_token_lifecycle(self):
        """Test JWT token creation, verification, and expiration"""
        # Create a valid JWT token
        payload = {
            "user_id": "jwt_test_user",
            "email": "jwt@example.com",
            "name": "JWT Test User",
            "exp": time.time() + 3600  # 1 hour from now
        }
        token = jwt.encode(payload, "test_jwt_secret", algorithm="HS256")
        
        # Add user to database
        test_db.users["jwt_test_user"] = {
            "_id": "jwt_test_user",
            "email": "jwt@example.com",
            "name": "JWT Test User",
            "picture": "https://example.com/jwt.jpg"
        }
        
        # Verify token is valid
        verify_response = client.get(f"/verify?token={token}")
        assert verify_response.status_code == 200
        
        verify_data = verify_response.json()
        assert verify_data["valid"] == True
        assert verify_data["user"]["email"] == "jwt@example.com"
        
        # Test with expired token
        expired_payload = {
            "user_id": "jwt_test_user",
            "email": "jwt@example.com",
            "name": "JWT Test User",
            "exp": time.time() - 3600  # 1 hour ago
        }
        expired_token = jwt.encode(expired_payload, "test_jwt_secret", algorithm="HS256")
        
        expired_response = client.get(f"/verify?token={expired_token}")
        assert expired_response.status_code == 401
        assert "Token expired" in expired_response.json()["detail"]
