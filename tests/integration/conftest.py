import pytest
import httpx
import os
from motor.motor_asyncio import AsyncIOMotorClient
import asyncio

# Use the service name defined in docker-compose
BACKEND_URL = "http://backend:8000/api"
MONGO_URL = os.getenv("DATABASE_URL", "mongodb://mongodb:27017")
DB_NAME = "translatar_db"

#@pytest.fixture(scope="session")
#def event_loop():
#    """Use a single event loop for all async tests."""
#    loop = asyncio.get_event_loop()
#    yield loop
#    loop.close()


@pytest.fixture(scope="function")
async def test_db():
    """Provide a connection to the same MongoDB used by the backend."""
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    yield db

    # Cleanup after all tests are done
    await client.drop_database(DB_NAME)
    client.close()

@pytest.fixture(scope ="function")
async def translations_collection(test_db):
    """Return the translations collection and clean it before each test."""
    collection = test_db.get_collection("translations")

    # Clean before each test
    await collection.delete_many({})
    yield collection
    await collection.delete_many({})