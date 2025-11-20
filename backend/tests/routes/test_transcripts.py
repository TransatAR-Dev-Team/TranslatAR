from datetime import datetime, timedelta
from fastapi.testclient import TestClient
import pytest

from main import app


@pytest.fixture
def fake_transcripts_collection():
    now = datetime.utcnow()
    documents = [
        {"_id": object(), "timestamp": now, "original_text": "A"},
        {"_id": object(), "timestamp": now - timedelta(minutes=1), "original_text": "B"},
    ]

    class FakeCollection:
        def find(self, query):
            docs = list(documents)

            if "timestamp" in query and "$gte" in query["timestamp"]:
                gte = query["timestamp"]["$gte"]
                docs = [doc for doc in docs if doc["timestamp"] >= gte]

            return AsyncCursor(docs)

    class AsyncCursor:
        def __init__(self, docs):
            self._docs = docs
            self._limit = len(docs)

        def sort(self, key, direction):
            reverse = direction == -1
            self._docs = sorted(self._docs, key=lambda doc: doc[key], reverse=reverse)
            return self

        def limit(self, value):
            self._limit = value
            return self

        def __aiter__(self):
            async def generator():
                for doc in self._docs[: self._limit]:
                    yield dict(doc)
            return generator()

    return FakeCollection()


@pytest.fixture(autouse=True)
def override_db(monkeypatch, fake_transcripts_collection):
    monkeypatch.setattr(
        app.state.db,
        "get_collection",
        lambda name: fake_transcripts_collection,
    )
    yield


def test_get_transcripts_success():
    with TestClient(app) as client:
        response = client.post("/api/transcripts", json={"limit": 1})
        assert response.status_code == 200
        body = response.json()
        assert len(body) == 1
        assert body[0]["original_text"] == "A"


def test_get_transcripts_validation_error():
    with TestClient(app) as client:
        response = client.post("/api/transcripts", json={"limit": 0})
        assert response.status_code == 422


def test_get_transcripts_service_failure(monkeypatch):
    async def boom(*_, **__):
        raise RuntimeError("failure")

    monkeypatch.setattr("routes.transcripts.fetch_transcripts", boom)

    with TestClient(app) as client:
        response = client.post("/api/transcripts", json={})
        assert response.status_code == 500
        assert "Failed to load transcripts" in response.json()["detail"]