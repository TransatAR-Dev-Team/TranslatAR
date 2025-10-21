from fastapi.testclient import TestClient
import pytest
import main
from main import app, SettingsModel


class FakeSettingsCollection:
    def __init__(self):
        self._doc = None

    async def find_one(self, _filter: dict):
        return self._doc

    async def replace_one(self, _filter: dict, replacement: dict, upsert: bool):
        self._doc = dict(replacement)
        return type("Result", (), {"acknowledged": True, "modified_count": 1})


@pytest.fixture(autouse=True)
def override_settings_collection():
    # Override Mongo collection with in-memory fake per test
    main.settings_collection = FakeSettingsCollection()
    yield


def test_get_settings_returns_defaults_when_empty():
    # Test case 1: Get initial settings (default values)
    client = TestClient(app)
    resp = client.get("/api/settings")
    assert resp.status_code == 200
    data = resp.json()
    assert data["settings"] == SettingsModel().model_dump()


def test_post_then_get_returns_saved_values():
    # Test case 2: Get saved settings
    client = TestClient(app)
    payload = SettingsModel(source_language="ko", target_language="en").model_dump()
    resp_post = client.post("/api/settings", json=payload)
    assert resp_post.status_code == 200

    resp_get = client.get("/api/settings")
    assert resp_get.status_code == 200
    assert resp_get.json()["settings"] == payload


def test_post_response_reflects_updates():
    # Test case 3: Check POST response reflects updates
    client = TestClient(app)
    payload = SettingsModel(source_language="ja", target_language="fr").model_dump()
    resp = client.post("/api/settings", json=payload)
    assert resp.status_code == 200
    assert resp.json()["settings"] == payload


def test_persistence_post_followed_by_get():
    # Test case 4: Check data persistence (POST followed by GET)
    client = TestClient(app)
    payload = SettingsModel(
        source_language="ko",
        target_language="en",
        chunk_duration_seconds=4.0,
    ).model_dump()
    client.post("/api/settings", json=payload)
    resp_get = client.get("/api/settings")
    assert resp_get.status_code == 200
    assert resp_get.json()["settings"] == payload