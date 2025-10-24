from fastapi import APIRouter, Request, HTTPException, Depends
from fastapi.responses import RedirectResponse
from urllib.parse import urlencode
import os
import httpx
import inspect
import jwt
import time
from typing import Optional

router = APIRouter()

# JWT dependency for protected routes
def get_current_user(authorization: Optional[str] = None):
    """Verify JWT token and return user info."""
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header missing")
    
    try:
        # Extract token from "Bearer <token>"
        token = authorization.split(" ")[1] if " " in authorization else authorization
        decoded = jwt.decode(token, os.getenv("JWT_SECRET"), algorithms=["HS256"])
        return decoded
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")


@router.get("/google")
def google_login():
    """Create Google OAuth Login URL"""
    params = {
        "client_id": os.getenv("GOOGLE_CLIENT_ID"),
        "redirect_uri": os.getenv("GOOGLE_REDIRECT_URI"),
        "response_type": "code",
        "scope": "openid email profile",
        "access_type": "offline",
        "prompt": "consent"
    }
    url = f"https://accounts.google.com/o/oauth2/v2/auth?{urlencode(params)}"
    return {"auth_url": url}


@router.get("/google/callback")
async def google_callback(request: Request, code: str):
    """Handle Google OAuth Callback"""
    token_data = {
        "code": code,
        "client_id": os.getenv("GOOGLE_CLIENT_ID"),
        "client_secret": os.getenv("GOOGLE_CLIENT_SECRET"),
        "redirect_uri": os.getenv("GOOGLE_REDIRECT_URI"),
        "grant_type": "authorization_code"
    }

    async def _json_maybe_async(response):
        """Return response.json(), awaiting if the mocked method is async in tests."""
        data = response.json()
        if inspect.iscoroutine(data):
            data = await data
        return data

    async with httpx.AsyncClient() as client:
        # Exchange code for access token
        r = await client.post("https://oauth2.googleapis.com/token", data=token_data)
        token_info = await _json_maybe_async(r)
        access_token = token_info.get("access_token")

        if not access_token:
            raise HTTPException(status_code=400, detail="Failed to obtain access token")

        # Get user info from Google
        user_info_response = await client.get(
            "https://www.googleapis.com/oauth2/v1/userinfo",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        user_info = await _json_maybe_async(user_info_response)

    if "email" not in user_info:
        raise HTTPException(status_code=400, detail="Invalid Google login")

    # Save user to database
    db = request.app.state.db
    user = db.create_or_update_user(user_info)

    # Create JWT token
    payload = {
        "user_id": str(user["_id"]),
        "email": user_info["email"],
        "name": user_info.get("name", ""),
        "exp": time.time() + 86400  # 24 hours
    }
    token = jwt.encode(payload, os.getenv("JWT_SECRET"), algorithm="HS256")

    # Return token and user info
    return {
        "jwt": token,
        "user": {
            "id": str(user["_id"]),
            "email": user_info["email"],
            "name": user_info.get("name", ""),
            "picture": user_info.get("picture", "")
        }
    }


@router.get("/verify")
def verify_token(token: str):
    """Test JWT Token Validity"""
    try:
        decoded = jwt.decode(token, os.getenv("JWT_SECRET"), algorithms=["HS256"])
        return {"valid": True, "decoded": decoded}
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")


@router.get("/me")
def get_current_user_info(request: Request, authorization: str):
    """Get current user information from JWT token"""
    user_data = get_current_user(authorization)
    
    # Get full user info from database
    db = request.app.state.db
    user = db.get_user_by_id(user_data["user_id"])
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {
        "id": str(user["_id"]),
        "email": user["email"],
        "name": user.get("name", ""),
        "picture": user.get("picture", ""),
        "settings": user.get("settings", {})
    }

