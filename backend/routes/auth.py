import logging
import os

from fastapi import APIRouter, Body, HTTPException, Request, status
from google.auth.transport import requests as google_requests
from google.oauth2 import id_token

from security.auth import create_access_token
from services.user_service import get_or_create_user_by_google_id

logger = logging.getLogger(__name__)

router = APIRouter()

USERS_COLLECTION = os.getenv("USERS_COLLECTION", "users")
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")


@router.post("/google/login")
async def google_login(request: Request, token: str = Body(..., embed=True)):
    logger.info("Received request for Google login.")
    if not GOOGLE_CLIENT_ID:
        logger.error(
            "CRITICAL: GOOGLE_CLIENT_ID is not configured." "Did you read our setup instructions?"
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Google Client ID is not configured on the server.",
        )

    try:
        logger.info("Verifying Google ID token...")
        idinfo = id_token.verify_oauth2_token(token, google_requests.Request(), GOOGLE_CLIENT_ID)

        googleId = idinfo["sub"]
        email = idinfo["email"]
        logger.info("Successfully verified Google token for email: %s", email)

    except ValueError as e:
        logger.warning("Invalid Google token received: %s", e)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Google token",
        ) from e

    db = request.app.state.db
    users_collection = db.get_collection(USERS_COLLECTION)

    user = await get_or_create_user_by_google_id(users_collection, googleId, email)

    if not user:
        logger.error("Failed to retrieve or create user for Google ID: %s", googleId)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Could not create or retrieve user with Google ID {googleId}.",
        )

    logger.info("User found or created with internal ID: %s", user["_id"])
    access_token = create_access_token(data={"sub": str(user["_id"])})
    logger.info("Successfully created and returned JWT for user: %s", user["_id"])

    return {"access_token": access_token, "token_type": "bearer"}
