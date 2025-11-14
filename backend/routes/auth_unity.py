import logging
import os

import httpx
from fastapi import APIRouter, HTTPException, Request, status
from google.auth.transport import requests as google_requests
from google.oauth2 import id_token
from pydantic import BaseModel

from security.auth import create_access_token
from services.user_service import get_or_create_user_by_google_id

logger = logging.getLogger(__name__)


# --- Pydantic Models ---
class DeviceStartResponse(BaseModel):
    user_code: str
    verification_url: str
    device_code: str
    interval: int
    expires_in: int


class DevicePollRequest(BaseModel):
    device_code: str


class DevicePollResponse(BaseModel):
    status: str
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
    logger.info("Unity device flow started.")
    if not GOOGLE_CLIENT_ID_UNITY:
        logger.error("CRITICAL: GOOGLE_CLIENT_ID_UNITY is not configured.")
        raise HTTPException(status_code=500, detail="Google Client ID for Unity is not configured.")

    payload = {"client_id": GOOGLE_CLIENT_ID_UNITY, "scope": "email profile openid"}

    async with httpx.AsyncClient() as client:
        try:
            logger.info("Requesting device code from Google.")
            response = await client.post(GOOGLE_DEVICE_CODE_URL, data=payload)
            response.raise_for_status()
            data = response.json()
            logger.info("Successfully received device code from Google: %s", data["user_code"])
            return DeviceStartResponse(**data)
        except httpx.HTTPStatusError as e:
            logger.error("Google returned an error during device flow start: %s", e.response.text)
            raise HTTPException(
                status_code=e.response.status_code,
                detail=f"Failed to get device code from Google: {e.response.text}",
            ) from e
        except Exception as e:
            logger.error(
                "An unexpected error occurred during device flow start: %s", e, exc_info=True
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"An unexpected error occurred: {str(e)}",
            ) from e


@router.post("/poll", response_model=DevicePollResponse)
async def poll_for_token(request: Request, poll_request: DevicePollRequest):
    logger.info("Polling for token with device code.")
    if not GOOGLE_CLIENT_ID_UNITY or not GOOGLE_CLIENT_SECRET_UNITY:
        logger.error("CRITICAL: Unity Google client credentials are not configured.")
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
        data = response.json()

        # Google uses error codes to signal status
        error = data.get("error")

        if error == "authorization_pending":
            logger.info("Authorization is still pending for device code.")
            return DevicePollResponse(status="authorization_pending")
        if error in ("slow_down", "expired_token", "access_denied"):
            logger.warning("Received status '%s' from Google during polling.", error)
            return DevicePollResponse(status=error)

        response.raise_for_status()  # Raise for other unexpected errors

        # --- Success: Tokens received. Verify ID and process user. ---
        try:
            logger.info("Token received. Verifying Google ID token.")
            idinfo = id_token.verify_oauth2_token(
                data["id_token"], google_requests.Request(), GOOGLE_CLIENT_ID_UNITY
            )
            google_id = idinfo["sub"]
            email = idinfo["email"]
            logger.info("Successfully verified token for user: %s", email)
        except ValueError as e:
            logger.error("Invalid Google ID token received during device flow: %s", e)
            raise HTTPException(status_code=401, detail=f"Invalid Google ID token: {e}") from e

        db = request.app.state.db
        users_collection = db.get_collection(USERS_COLLECTION)

        user = await get_or_create_user_by_google_id(users_collection, google_id, email)

        if not user:
            logger.error("Failed to get or create user for Google ID: %s", google_id)
            raise HTTPException(status_code=500, detail="Could not create or retrieve user.")

        app_access_token = create_access_token(data={"sub": str(user["_id"])})

        logger.info("Successfully completed device flow for user: %s", email)
        return DevicePollResponse(status="completed", access_token=app_access_token)
