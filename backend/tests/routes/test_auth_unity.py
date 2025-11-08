from types import SimpleNamespace

import httpx
import pytest
from fastapi.testclient import TestClient

from main import app, db
from routes import auth_unity
from security import auth as security_auth

# --- Fixtures ---


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


@pytest.fixture
def fake_users_collection():
    class _Fake:
        def __init__(self):
            self._docs = {}

        async def find_one(self, query: dict):
            return self._docs.get(query.get("googleId"))

        async def insert_one(self, doc: dict):
            gid = doc.get("googleId")
            self._docs[gid] = {"_id": f"uid_{gid}", **doc}
            return SimpleNamespace(acknowledged=True)

    return _Fake()


@pytest.fixture(autouse=True)
def override_db_collection(monkeypatch, fake_users_collection):
    monkeypatch.setattr(db, "get_collection", lambda name: fake_users_collection)


# --- Tests for /start endpoint ---


def test_start_device_flow_success(client, mocker, monkeypatch):
    monkeypatch.setattr(auth_unity, "GOOGLE_CLIENT_ID_UNITY", "fake-id")

    class MockClient:
        async def __aenter__(self):
            return self

        async def __aexit__(self, *args):
            pass

        async def post(self, *args, **kwargs):
            class MockResponse:
                status_code = 200

                def raise_for_status(self):
                    pass

                async def json(self):
                    return {
                        "device_code": "c",
                        "user_code": "uc",
                        "verification_url": "url",
                        "expires_in": 1,
                        "interval": 5,
                    }

            return MockResponse()

    mocker.patch("httpx.AsyncClient", MockClient)

    response = client.post("/api/auth/device/start")

    assert response.status_code == 200
    assert response.json()["user_code"] == "uc"


def test_start_device_flow_google_error(client, mocker, monkeypatch):
    monkeypatch.setattr(auth_unity, "GOOGLE_CLIENT_ID_UNITY", "fake-id")

    class MockClient:
        async def __aenter__(self):
            return self

        async def __aexit__(self, *args):
            pass

        async def post(self, *args, **kwargs):
            class MockResponse:
                status_code = 400
                text = "Bad Request"

                def raise_for_status(self):
                    raise httpx.HTTPStatusError("Error", request=mocker.Mock(), response=self)

                async def json(self):
                    return {}

            return MockResponse()

    mocker.patch("httpx.AsyncClient", MockClient)

    response = client.post("/api/auth/device/start")

    assert response.status_code == 400


# --- Tests for /poll endpoint ---


def test_poll_authorization_pending(client, mocker, monkeypatch):
    monkeypatch.setattr(auth_unity, "GOOGLE_CLIENT_ID_UNITY", "fake-id")
    monkeypatch.setattr(auth_unity, "GOOGLE_CLIENT_SECRET_UNITY", "fake-secret")

    class MockClient:
        async def __aenter__(self):
            return self

        async def __aexit__(self, *args):
            pass

        async def post(self, *args, **kwargs):
            class MockResponse:
                def raise_for_status(self):
                    pass

                async def json(self):
                    return {"error": "authorization_pending"}

            return MockResponse()

    mocker.patch("httpx.AsyncClient", MockClient)

    response = client.post("/api/auth/device/poll", json={"device_code": "any"})

    assert response.status_code == 200
    assert response.json()["status"] == "authorization_pending"


def test_poll_success_new_user(client, mocker, monkeypatch, fake_users_collection):
    monkeypatch.setattr(security_auth, "JWT_SECRET_KEY", "test-secret")
    monkeypatch.setattr(auth_unity, "GOOGLE_CLIENT_ID_UNITY", "fake-id")
    monkeypatch.setattr(auth_unity, "GOOGLE_CLIENT_SECRET_UNITY", "fake-secret")

    mocker.patch(
        "google.oauth2.id_token.verify_oauth2_token",
        return_value={"sub": "gid_123", "email": "a@b.com"},
    )

    class MockClient:
        async def __aenter__(self):
            return self

        async def __aexit__(self, *args):
            pass

        async def post(self, *args, **kwargs):
            class MockResponse:
                def raise_for_status(self):
                    pass

                async def json(self):
                    return {"id_token": "fake_google_id_token"}

            return MockResponse()

    mocker.patch("httpx.AsyncClient", MockClient)

    response = client.post("/api/auth/device/poll", json={"device_code": "any"})

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "completed"
    assert "access_token" in data
    assert len(fake_users_collection._docs) == 1


def test_poll_success_existing_user(client, mocker, monkeypatch, fake_users_collection):
    monkeypatch.setattr(security_auth, "JWT_SECRET_KEY", "test-secret")
    monkeypatch.setattr(auth_unity, "GOOGLE_CLIENT_ID_UNITY", "fake-id")
    monkeypatch.setattr(auth_unity, "GOOGLE_CLIENT_SECRET_UNITY", "fake-secret")

    fake_users_collection._docs["gid_456"] = {"_id": "mid_abc", "googleId": "gid_456"}

    mocker.patch(
        "google.oauth2.id_token.verify_oauth2_token",
        return_value={"sub": "gid_456", "email": "c@d.com"},
    )

    class MockClient:
        async def __aenter__(self):
            return self

        async def __aexit__(self, *args):
            pass

        async def post(self, *args, **kwargs):
            class MockResponse:
                def raise_for_status(self):
                    pass

                async def json(self):
                    return {"id_token": "fake_google_id_token"}

            return MockResponse()

    mocker.patch("httpx.AsyncClient", MockClient)

    response = client.post("/api/auth/device/poll", json={"device_code": "any"})

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "completed"
    assert "access_token" in data
    assert len(fake_users_collection._docs) == 1
