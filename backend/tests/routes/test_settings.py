from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient
from pymongo.errors import ConnectionFailure

from main import app  # Import the app instance
from models.settings import SettingsModel


@pytest.fixture
def fake_settings_collection():
    """A mock of the Pymongo collection for in-memory testing."""

    class _Fake:
        def __init__(self):
            self._doc = None  # This will store our single settings document

        async def find_one(self, _filter: dict):
            # Return a copy of the document to mimic database behavior
            return self._doc.copy() if self._doc else None

        async def replace_one(self, _filter: dict, replacement: dict, upsert: bool):
            # Store a copy of the replacement document
            self._doc = dict(replacement)
            return SimpleNamespace(acknowledged=True, modified_count=1)

    return _Fake()


@pytest.fixture(autouse=True)
def override_db_dependency(monkeypatch, fake_settings_collection):
    """
    This fixture intercepts the database call within the endpoint and provides
    our in-memory mock collection instead of a real one.
    """
    monkeypatch.setattr(app.state.db, "get_collection", lambda name: fake_settings_collection)
    yield


def test_get_settings_returns_defaults_when_empty():
    with TestClient(app) as client:
        resp = client.get("/api/settings")
        assert resp.status_code == 200
        # Check against the Pydantic model's default values
        assert resp.json()["settings"] == SettingsModel().model_dump()


def test_post_then_get_returns_saved_values():
    with TestClient(app) as client:
        # Define a payload with custom settings
        payload = SettingsModel(source_language="ko", target_language="en").model_dump()

        # 1. POST the new settings
        resp_post = client.post("/api/settings", json=payload)
        assert resp_post.status_code == 200
        assert resp_post.json()["settings"] == payload

        # 2. GET the settings again to ensure they were persisted in our mock
        resp_get = client.get("/api/settings")
        assert resp_get.status_code == 200
        assert resp_get.json()["settings"] == payload


def test_post_invalid_type_returns_422():
    with TestClient(app) as client:
        # Create a payload with an incorrect data type
        bad_payload = {
            **SettingsModel().model_dump(),
            "target_sample_rate": "this-is-not-an-integer",
        }
        resp = client.post("/api/settings", json=bad_payload)
        assert resp.status_code == 422


@pytest.mark.asyncio
async def test_get_settings_db_error_returns_500(monkeypatch, fake_settings_collection):
    # Simulate a database failure for the find_one operation
    async def mock_find_one_failure(_):
        raise ConnectionFailure("Database is down")

    monkeypatch.setattr(fake_settings_collection, "find_one", mock_find_one_failure)

    with TestClient(app) as client:
        resp = client.get("/api/settings")
        assert resp.status_code == 500
        assert "Failed to retrieve settings" in resp.json()["detail"]


@pytest.mark.asyncio
async def test_post_settings_db_error_returns_500(monkeypatch, fake_settings_collection):
    # Simulate a database failure for the replace_one operation
    async def mock_replace_one_failure(_, __, ___):
        raise ConnectionFailure("Database is down")

    monkeypatch.setattr(fake_settings_collection, "replace_one", mock_replace_one_failure)

    with TestClient(app) as client:
        resp = client.post("/api/settings", json=SettingsModel().model_dump())
        assert resp.status_code == 500
        assert "Failed to save settings" in resp.json()["detail"]
