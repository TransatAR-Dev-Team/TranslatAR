# tests/integration/test_api.py
import pytest
import httpx

BACKEND_URL = "http://backend:8000/api"

@pytest.mark.asyncio
async def test_db_hello_endpoint():
    """
    A trivial integration test to verify that the backend service
    can connect to the database and respond to a request.
    
    The 'wait_for_backend' fixture ensures this test only runs
    when the service is confirmed to be healthy.
    """
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BACKEND_URL}/db-hello", timeout=10.0)

        # 1. Check if the HTTP request was successful
        assert response.status_code == 200

        # 2. Check if the response body is what we expect
        expected_json = {"message": "Hello from MongoDB!"}
        assert response.json() == expected_json
