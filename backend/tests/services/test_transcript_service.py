from datetime import datetime, timedelta
import pytest

from services.transcript_service import fetch_transcripts


class FakeDB:
    def __init__(self, documents):
        self._documents = documents

    def get_collection(self, name):
        assert name == "translations"
        return FakeCollection(self._documents)


class FakeCollection:
    def __init__(self, documents):
        self._documents = documents

    def find(self, query):
        docs = list(self._documents)

        if "timestamp" in query:
            gte = query["timestamp"].get("$gte")
            if gte:
                docs = [doc for doc in docs if doc["timestamp"] >= gte]

        if "userId" in query:
            docs = [doc for doc in docs if doc.get("userId") == query["userId"]]

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


@pytest.mark.asyncio
async def test_fetch_transcripts_returns_sorted_and_limited():
    now = datetime.utcnow()
    docs = [
        {"_id": object(), "timestamp": now, "text": "latest"},
        {"_id": object(), "timestamp": now - timedelta(minutes=1), "text": "older"},
        {"_id": object(), "timestamp": now - timedelta(minutes=2), "text": "oldest"},
    ]
    db = FakeDB(docs)

    result = await fetch_transcripts(db, limit=2)

    assert len(result) == 2
    assert result[0]["text"] == "latest"
    assert result[1]["text"] == "older"
    assert all(isinstance(item["_id"], str) for item in result)


@pytest.mark.asyncio
async def test_fetch_transcripts_applies_filters():
    now = datetime.utcnow()
    docs = [
        {"_id": object(), "timestamp": now, "userId": "alice"},
        {"_id": object(), "timestamp": now - timedelta(days=1), "userId": "bob"},
    ]
    db = FakeDB(docs)

    result = await fetch_transcripts(
        db,
        since=now - timedelta(hours=12),
        user_id="alice",
    )

    assert len(result) == 1
    assert result[0]["userId"] == "alice"