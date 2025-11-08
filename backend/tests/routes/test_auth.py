from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient

import main
from main import app
from models.settings import SettingsModel
from security.auth import get_current_user

# --- Test Setup for Authentication ---
FAKE_USER = {"_id": "fakeuserid123", "email": "settings_test@example.com"}


def override_get_current_user():
    return FAKE_USER


# --- Fixture for an Authenticated Client ---
@pytest.fixture
def authenticated_client() -> TestClient:
    """Returns a TestClient with the authentication override in place."""
    app.dependency_overrides[get_current_user] = override_get_current_user
    yield TestClient(app)
    # Clean up after the test
    app.dependency_overrides.clear()


@pytest.fixture
def fake_settings_collection():
    class _Fake:
        def __init__(self):
            self._doc = None

        async def find_one(self, _filter: dict):
            return self._doc

        async def replace_one(self, _f: dict, r: dict, upsert: bool):
            self._doc = dict(r)
            return SimpleNamespace(acknowledged=True)

    return _Fake()


@pytest.fixture(autouse=True)
def override_db_collection(fake_settings_collection, monkeypatch):
    monkeypatch.setattr(main, "settings_collection", fake_settings_collection)
    yield


def test_get_settings_as_authenticated_user(authenticated_client):
    resp = authenticated_client.get("/api/settings")
    assert resp.status_code == 200
    assert resp.json()["settings"] == SettingsModel().model_dump()


def test_post_then_get_as_authenticated_user(authenticated_client):
    payload = SettingsModel(source_language="ko").model_dump()
    resp_post = authenticated_client.post("/api/settings", json=payload)
    assert resp_post.status_code == 200

    resp_get = authenticated_client.get("/api/settings")
    assert resp_get.status_code == 200
    assert resp_get.json()["settings"] == payload


def test_post_invalid_type_returns_422(authenticated_client):
    bad_payload = {**SettingsModel().model_dump(), "target_sample_rate": "not-an-int"}
    resp = authenticated_client.post("/api/settings", json=bad_payload)
    assert resp.status_code == 422
