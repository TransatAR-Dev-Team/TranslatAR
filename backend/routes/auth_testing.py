import logging

from fastapi import APIRouter, HTTPException

from config.database import db
from security.auth import create_access_token
from services.user_service import get_or_create_user_by_google_id

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/get-token")
async def get_test_token():
    """
    Creates/retrieves a test user and returns a valid JWT.
    This endpoint should only be active in a 'test' environment.
    """
    test_google_id = "test_user_google_id_integration"
    test_email = "test@integration.com"

    users_collection = db.get_collection("users")
    user = await get_or_create_user_by_google_id(users_collection, test_google_id, test_email)

    if not user:
        raise HTTPException(status_code=500, detail="Could not create or retrieve test user.")

    access_token = create_access_token(data={"sub": str(user["_id"])})
    logger.info(f"Generated test token for user {user['_id']}")
    return {"access_token": access_token}
