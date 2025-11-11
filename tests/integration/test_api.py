import pytest
import httpx

BACKEND_URL = "http://backend:8000/api"

@pytest.mark.asyncio
async def test_health_endpoint():
    """
    A trivial integration test to verify that the backend service
    can connect to the database and respond to a request.
    """
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BACKEND_URL}/health", timeout=10.0)

        assert response.status_code == 200
        assert response.json().get("status") == "ok"
        # THE FIX IS HERE: Change "database" to "database_status"
        assert response.json().get("database_status") == "connected"
