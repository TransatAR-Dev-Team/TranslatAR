# tests/integration/conftest.py (updated)
import pytest
import httpx
import asyncio
import time

# Use the service name from docker-compose.
BACKEND_URL = "http://backend:8000/api"

@pytest.fixture(scope="session")
def event_loop():
    """Force the event loop to be the same for the whole session."""
    loop = asyncio.get_event_loop()
    yield loop
    loop.close()
