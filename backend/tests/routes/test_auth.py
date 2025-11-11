from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient

from main import app, db
from routes import auth as auth_router
from security import auth as security_auth

# --- Fixtures ---


@pytest.fixture
def client() -> TestClient:
    """Provides a test client for the FastAPI application."""
    return TestClient(app)


@pytest.fixture
def fake_users_collection():
    """Provides an in-memory mock of the users collection."""

    class _Fake:
        def __init__(self):
            self._docs = {}

        async def find_one(self, query: dict):
            return self._docs.get(query.get("googleId"))

        async def insert_one(self, doc: dict):
            gid = doc.get("googleId")
            # Simulate MongoDB adding an _id
            self._docs[gid] = {"_id": f"uid_{gid}", **doc}
            return SimpleNamespace(acknowledged=True)

    return _Fake()


@pytest.fixture(autouse=True)
def override_db_collection(monkeypatch, fake_users_collection):
    """Overrides the database dependency to use the fake collection."""
    monkeypatch.setattr(db, "get_collection", lambda name: fake_users_collection)


# --- Tests for Google Login ---


def test_google_login_success_new_user(client, mocker, monkeypatch, fake_users_collection):
    # Setup mocks
    monkeypatch.setattr(auth_router, "GOOGLE_CLIENT_ID", "fake-client-id")
    monkeypatch.setattr(security_auth, "JWT_SECRET_KEY", "test-secret")
    mocker.patch(
        "google.oauth2.id_token.verify_oauth2_token",
        return_value={"sub": "new_gid_123", "email": "new@test.com"},
    )

    # Make the API call
    response = client.post("/api/auth/google/login", json={"token": "fake_google_token"})

    # Assertions
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    # Verify a new user was created in our mock collection
    assert len(fake_users_collection._docs) == 1
    assert fake_users_collection._docs.get("new_gid_123") is not None


def test_google_login_success_existing_user(client, mocker, monkeypatch, fake_users_collection):
    # Pre-populate the mock collection with an existing user
    existing_google_id = "existing_gid_456"
    fake_users_collection._docs[existing_google_id] = {
        "_id": "existing_mongo_id",
        "googleId": existing_google_id,
    }

    # Setup mocks
    monkeypatch.setattr(auth_router, "GOOGLE_CLIENT_ID", "fake-client-id")
    monkeypatch.setattr(security_auth, "JWT_SECRET_KEY", "test-secret")
    mocker.patch(
        "google.oauth2.id_token.verify_oauth2_token",
        return_value={"sub": existing_google_id, "email": "existing@test.com"},
    )

    # Make the API call
    response = client.post("/api/auth/google/login", json={"token": "fake_google_token"})

    # Assertions
    assert response.status_code == 200
    assert "access_token" in response.json()
    # Verify no new user was created
    assert len(fake_users_collection._docs) == 1


def test_google_login_invalid_token(client, mocker, monkeypatch):
    # Setup mocks
    monkeypatch.setattr(auth_router, "GOOGLE_CLIENT_ID", "fake-client-id")
    # Mock the Google token verification to raise a ValueError
    mocker.patch(
        "google.oauth2.id_token.verify_oauth2_token",
        side_effect=ValueError("Invalid token"),
    )

    response = client.post("/api/auth/google/login", json={"token": "invalid_token"})

    assert response.status_code == 401
    assert "Invalid Google token" in response.json()["detail"]
