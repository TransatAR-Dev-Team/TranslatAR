import os

from fastapi import APIRouter, Body, HTTPException, Request, status
from google.auth.transport import requests as google_requests
from google.oauth2 import id_token

from security.auth import create_access_token
from services.user_service import get_or_create_user_by_google_id

router = APIRouter()

USERS_COLLECTION = os.getenv("USERS_COLLECTION", "users")
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")


@router.post("/google/login")
async def google_login(request: Request, token: str = Body(..., embed=True)):
    if not GOOGLE_CLIENT_ID:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Google Client ID is not configured on the server.",
        )

    try:
        # Verify the ID token with Google's servers
        idinfo = id_token.verify_oauth2_token(token, google_requests.Request(), GOOGLE_CLIENT_ID)

        googleId = idinfo["sub"]
        email = idinfo["email"]

    except ValueError as e:
        # The token is invalid
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Google token",
        ) from e

    db = request.app.state.db
    users_collection = db.get_collection(USERS_COLLECTION)

    user = await get_or_create_user_by_google_id(users_collection, googleId, email)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not create or retrieve user from the database.",
        )

    access_token = create_access_token(data={"sub": str(user["_id"])})

    return {"access_token": access_token, "token_type": "bearer"}
