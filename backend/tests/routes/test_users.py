import pytest
from bson import ObjectId
from datetime import datetime, UTC
from fastapi.testclient import TestClient

from main import app
from security import auth as security_auth
from security.auth import get_current_user


# --- Fixtures ---


@pytest.fixture
def client() -> TestClient:
    """Provides a test client for the FastAPI application."""
    return TestClient(app)


@pytest.fixture
def mock_user():
    """Provides a mock user document."""
    return {
        "_id": ObjectId(),
        "googleId": "test_google_id_123",
        "email": "testuser@example.com",
        "username": "testuser",
        "createdAt": datetime.now(UTC),
        "updatedAt": datetime.now(UTC),
    }


@pytest.fixture
def authenticated_client(mock_user):
    """Fixture that provides authentication override."""
    async def mock_get_current_user():
        return mock_user
    
    app.dependency_overrides[get_current_user] = mock_get_current_user
    yield
    app.dependency_overrides.clear()


# --- Tests with Mocked Authentication ---


def test_get_current_user_success(client, authenticated_client, mock_user):
    """
    Test that /users/me returns the current user when authenticated.
    Uses dependency override to simulate authentication.
    """
    response = client.get("/api/users/me")

    assert response.status_code == 200
    data = response.json()
    
    # Verify the response contains expected user data
    assert data["email"] == mock_user["email"]
    assert data["username"] == mock_user["username"]
    assert data["googleId"] == mock_user["googleId"]
    assert "_id" in data
    assert "createdAt" in data
    assert "updatedAt" in data


def test_get_current_user_unauthorized(client):
    """
    Test that /users/me returns 401 when no valid token is provided.
    """
    # Don't provide any Authorization header - the default oauth2_scheme will fail
    response = client.get("/api/users/me")
    
    assert response.status_code == 401
    assert "detail" in response.json()


def test_get_current_user_invalid_token(client):
    """
    Test that /users/me returns 401 when an invalid token is provided.
    """
    # Provide an Authorization header but with an invalid/expired token
    response = client.get(
        "/api/users/me",
        headers={"Authorization": "Bearer invalid_token_here"}
    )
    
    assert response.status_code == 401
    assert "detail" in response.json()


# --- Tests with Real JWT Tokens ---


def test_get_current_user_with_real_jwt(client, monkeypatch, mock_user):
    """
    Integration-style test that creates a real JWT token and validates
    the full authentication flow.
    """
    # Setup: Configure JWT secret
    monkeypatch.setattr(security_auth, "JWT_SECRET_KEY", "test-secret-key")
    
    # Mock the database lookup to return our user
    class FakeCollection:
        async def find_one(self, query):
            return mock_user
    
    class FakeDB:
        def __getitem__(self, name):
            return FakeCollection()
    
    # Patch the database in the app state
    monkeypatch.setattr(app.state, "db", FakeDB())
    
    # Create a real JWT token for this user
    from security.auth import create_access_token
    token = create_access_token(data={"sub": str(mock_user["_id"])})
    
    # Make the request with the real token
    response = client.get(
        "/api/users/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == mock_user["email"]
    assert data["username"] == mock_user["username"]


def test_get_current_user_jwt_missing_sub(client, monkeypatch):
    """
    Test that authentication fails when JWT token is missing the 'sub' claim.
    """
    monkeypatch.setattr(security_auth, "JWT_SECRET_KEY", "test-secret-key")
    
    # Create a token without a 'sub' field
    from jose import jwt
    from datetime import timedelta
    
    expire = datetime.now(UTC) + timedelta(minutes=15)
    to_encode = {"exp": expire}  # Missing 'sub'
    token = jwt.encode(to_encode, "test-secret-key", algorithm="HS256")
    
    response = client.get(
        "/api/users/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 401


def test_get_current_user_user_not_found_in_db(client, monkeypatch, mock_user):
    """
    Test that authentication fails when the user referenced in the JWT
    doesn't exist in the database.
    """
    monkeypatch.setattr(security_auth, "JWT_SECRET_KEY", "test-secret-key")
    
    # Mock the database to return None (user not found)
    class FakeCollection:
        async def find_one(self, query):
            return None
    
    class FakeDB:
        def __getitem__(self, name):
            return FakeCollection()
    
    monkeypatch.setattr(app.state, "db", FakeDB())
    
    from security.auth import create_access_token
    token = create_access_token(data={"sub": str(mock_user["_id"])})
    
    response = client.get(
        "/api/users/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 401


# --- Edge Cases ---


def test_get_current_user_expired_token(client, monkeypatch, mock_user):
    """
    Test that authentication fails with an expired JWT token.
    """
    monkeypatch.setattr(security_auth, "JWT_SECRET_KEY", "test-secret-key")
    
    # Create an expired token
    from jose import jwt
    from datetime import timedelta
    
    expire = datetime.now(UTC) - timedelta(minutes=1)  # Already expired
    to_encode = {"sub": str(mock_user["_id"]), "exp": expire}
    token = jwt.encode(to_encode, "test-secret-key", algorithm="HS256")
    
    response = client.get(
        "/api/users/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 401


def test_get_current_user_nonexistent_objectid(client, monkeypatch):
    """
    Test that authentication fails when JWT contains a valid ObjectId format
    that doesn't correspond to any user in the database.
    """
    monkeypatch.setattr(security_auth, "JWT_SECRET_KEY", "test-secret-key")
    
    from security.auth import create_access_token
    # Use a valid ObjectId format that doesn't exist in the database
    nonexistent_id = "507f1f77bcf86cd799439011"
    token = create_access_token(data={"sub": nonexistent_id})
    
    # Mock the database to return None (user not found)
    class FakeCollection:
        async def find_one(self, query):
            return None
    
    class FakeDB:
        def __getitem__(self, name):
            return FakeCollection()
    
    monkeypatch.setattr(app.state, "db", FakeDB())
    
    response = client.get(
        "/api/users/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    # The endpoint should return 401 when user not found
    assert response.status_code == 401
