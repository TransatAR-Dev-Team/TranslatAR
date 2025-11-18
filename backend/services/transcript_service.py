from datetime import datetime
from typing import Any

from motor.motor_asyncio import AsyncIOMotorDatabase


async def fetch_transcripts(
    db: AsyncIOMotorDatabase,
    *,
    limit: int = 50,
    since: datetime | None = None,
    user_id: str | None = None,
) -> list[dict[str, Any]]:
    query: dict[str, Any] = {}
    if since:
        query["timestamp"] = {"$gte": since}
    if user_id:
        query["user_id"] = user_id  # use if user information is stored

    cursor = (
        db.get_collection("translations")
        .find(query)
        .sort("timestamp", -1)
        .limit(limit)
    )

    results: list[dict[str, Any]] = []
    async for doc in cursor:
        doc["_id"] = str(doc["_id"])
        results.append(doc)
    return results