from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient

import main
from main import app
from models.settings import SettingsModel


@pytest.fixture
def fake_settings_collection():
    class _Fake:
        def __init__(self):
            self._doc = None

        async def find_one(self, _filter: dict):
            return self._doc

        async def replace_one(self, _filter: dict, replacement: dict, upsert: bool):
            self._doc = dict(replacement)
            return SimpleNamespace(acknowledged=True, modified_count=1)

    return _Fake()


@pytest.fixture(autouse=True)
def override_settings_collection(fake_settings_collection, monkeypatch):
    # Replace the collection used by the backend with an in-memory mock
    monkeypatch.setattr(main, "settings_collection", fake_settings_collection, raising=False)
    yield


def test_get_settings_returns_defaults_when_empty():
    client = TestClient(app)
    resp = client.get("/api/settings")
    assert resp.status_code == 200
    assert resp.json()["settings"] == SettingsModel().model_dump()


def test_post_then_get_returns_saved_values():
    client = TestClient(app)
    payload = SettingsModel(source_language="ko", target_language="en").model_dump()
    resp_post = client.post("/api/settings", json=payload)
    assert resp_post.status_code == 200
    assert resp_post.json()["settings"] == payload  # Check POST response reflects updates

    resp_get = client.get("/api/settings")  # Get saved settings
    assert resp_get.status_code == 200
    assert resp_get.json()["settings"] == payload


# Failure cases


def test_post_invalid_type_returns_422():
    client = TestClient(app)
    bad_payload = {
        **SettingsModel().model_dump(),
        "target_sample_rate": "not-an-int",  # Type error
    }
    resp = client.post("/api/settings", json=bad_payload)
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_get_settings_db_error_returns_500(fake_settings_collection):
    async def boom(_):
        raise Exception("db down")

    fake_settings_collection.find_one = boom  # Force DB exception
    client = TestClient(app)
    resp = client.get("/api/settings")
    assert resp.status_code == 500


@pytest.mark.asyncio
async def test_post_settings_db_error_returns_500(fake_settings_collection):
    async def boom(_, __, ___):
        raise Exception("db down")

    fake_settings_collection.replace_one = boom  # Force DB exception
    client = TestClient(app)
    resp = client.post("/api/settings", json=SettingsModel().model_dump())
    assert resp.status_code == 500
