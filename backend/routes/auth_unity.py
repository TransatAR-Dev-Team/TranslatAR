import os
from datetime import UTC, datetime

import httpx
from fastapi import APIRouter, HTTPException, Request, status
from google.auth.transport import requests as google_requests
from google.oauth2 import id_token
from pydantic import BaseModel

from security.auth import create_access_token

# --- Pydantic Models ---


class DeviceStartResponse(BaseModel):
    """Data sent to Unity after starting the login flow."""

    user_code: str
    verification_url: str
    device_code: str
    interval: int
    expires_in: int


class DevicePollRequest(BaseModel):
    """Data Unity sends to our backend to check the login status."""

    device_code: str


class DevicePollResponse(BaseModel):
    """Data our backend sends to Unity while polling."""

    status: str  # e.g., "authorization_pending", "completed", "error"
    access_token: str | None = None
    token_type: str | None = "bearer"


# --- Router and Configuration ---

router = APIRouter()

GOOGLE_CLIENT_ID_UNITY = os.getenv("GOOGLE_CLIENT_ID_UNITY")
GOOGLE_CLIENT_SECRET_UNITY = os.getenv("GOOGLE_CLIENT_SECRET_UNITY")
GOOGLE_DEVICE_CODE_URL = "https://oauth2.googleapis.com/device/code"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
USERS_COLLECTION = os.getenv("USERS_COLLECTION", "users")


@router.post("/start", response_model=DeviceStartResponse)
async def start_device_flow():
    """
    Initiates the OAuth 2.0 device flow for limited input devices.
    This endpoint contacts Google to get a user code and verification URL.
    """
    if not GOOGLE_CLIENT_ID_UNITY:
        raise HTTPException(
            status_code=500,
            detail="Google Client ID for Unity is not configured on the server.",
        )

    payload = {"client_id": GOOGLE_CLIENT_ID_UNITY, "scope": "email profile openid"}

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(GOOGLE_DEVICE_CODE_URL, data=payload)
            response.raise_for_status()

            data = await response.json()

            return DeviceStartResponse(**data)
        except httpx.HTTPStatusError as e:
            raise HTTPException(
                status_code=e.response.status_code,
                detail=f"Failed to get device code from Google: {e.response.text}",
            ) from e
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"An unexpected error occurred: {str(e)}",
            ) from e


@router.post("/poll", response_model=DevicePollResponse)
async def poll_for_token(request: Request, poll_request: DevicePollRequest):
    """
    Polls Google's token endpoint on behalf of the device. If the user has
    authenticated, this exchanges the device_code for tokens, finds/creates a
    user in our DB, and returns our own application JWT.
    """
    if not GOOGLE_CLIENT_ID_UNITY or not GOOGLE_CLIENT_SECRET_UNITY:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Google client credentials for Unity are not configured.",
        )

    payload = {
        "client_id": GOOGLE_CLIENT_ID_UNITY,
        "client_secret": GOOGLE_CLIENT_SECRET_UNITY,
        "device_code": poll_request.device_code,
        "grant_type": "urn:ietf:params:oauth:grant-type:device_code",
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(GOOGLE_TOKEN_URL, data=payload)
        data = await response.json()

        # Google uses error codes to signal status
        error = data.get("error")
        if error == "authorization_pending":
            return DevicePollResponse(status="authorization_pending")
        if error in ("slow_down", "expired_token", "access_denied"):
            return DevicePollResponse(status=error)

        response.raise_for_status()  # Raise for other unexpected errors

        # --- Success: Tokens received. Verify ID and process user. ---
        try:
            idinfo = id_token.verify_oauth2_token(
                data["id_token"], google_requests.Request(), GOOGLE_CLIENT_ID_UNITY
            )
            google_id = idinfo["sub"]
            email = idinfo["email"]
        except ValueError as e:
            raise HTTPException(status_code=401, detail=f"Invalid Google ID token: {e}") from e

        # --- Find or create the user in our database ---
        db = request.app.state.db
        users_collection = db.get_collection(USERS_COLLECTION)
        user = await users_collection.find_one({"googleId": google_id})

        if not user:
            new_user_doc = {
                "googleId": google_id,
                "email": email,
                "username": email.split("@")[0],
                "createdAt": datetime.now(UTC),
                "updatedAt": datetime.now(UTC),
            }
            await users_collection.insert_one(new_user_doc)
            user = await users_collection.find_one({"googleId": google_id})

        if not user:
            raise HTTPException(status_code=500, detail="Could not create or retrieve user.")

        # --- Create and return our own application JWT ---
        app_access_token = create_access_token(data={"sub": str(user["_id"])})

        return DevicePollResponse(status="completed", access_token=app_access_token)
