from fastapi import APIRouter, Request, HTTPException, Depends
from fastapi.responses import RedirectResponse
from urllib.parse import urlencode
import os
import httpx
import jwt
import time
from typing import Optional
from pydantic import BaseModel

router = APIRouter()

# Pydantic models
class OneTapRequest(BaseModel):
    credential: str

# JWT dependency for protected routes
def get_current_user(authorization: Optional[str] = None):
    """Verify JWT token and return user info."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Authorization header missing or invalid")
    
    token = authorization.split(" ")[1]
    try:
        payload = jwt.decode(token, os.getenv("JWT_SECRET"), algorithms=["HS256"])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

@router.get("/google")
def google_login():
    """Initiate Google OAuth login."""
    client_id = os.getenv("GOOGLE_CLIENT_ID")
    redirect_uri = os.getenv("GOOGLE_REDIRECT_URI")
    
    if not client_id or not redirect_uri:
        raise HTTPException(status_code=500, detail="Google OAuth not configured")
    
    # Google OAuth parameters
    params = {
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "scope": "openid email profile",
        "response_type": "code",
        "access_type": "offline",
        "prompt": "consent"
    }
    
    # Build Google OAuth URL
    google_auth_url = f"https://accounts.google.com/o/oauth2/v2/auth?{urlencode(params)}"
    
    return RedirectResponse(url=google_auth_url)

@router.get("/google/callback")
async def google_callback(request: Request, code: str):
    """Handle Google OAuth callback."""
    try:
        client_id = os.getenv("GOOGLE_CLIENT_ID")
        client_secret = os.getenv("GOOGLE_CLIENT_SECRET")
        redirect_uri = os.getenv("GOOGLE_REDIRECT_URI")
        
        # Exchange authorization code for access token
        async with httpx.AsyncClient() as client:
            token_response = await client.post(
                "https://oauth2.googleapis.com/token",
                data={
                    "client_id": client_id,
                    "client_secret": client_secret,
                    "code": code,
                    "grant_type": "authorization_code",
                    "redirect_uri": redirect_uri,
                }
            )
            
            if token_response.status_code != 200:
                raise HTTPException(status_code=400, detail="Failed to exchange code for token")
            
            token_data = token_response.json()
            access_token = token_data.get("access_token")
            
            if not access_token:
                raise HTTPException(status_code=400, detail="No access token received")
            
            # Get user info from Google
            user_response = await client.get(
                "https://www.googleapis.com/oauth2/v2/userinfo",
                headers={"Authorization": f"Bearer {access_token}"}
            )
            
            if user_response.status_code != 200:
                raise HTTPException(status_code=400, detail="Failed to get user info")
            
            user_data = user_response.json()
            
            # Create JWT token for our application
            jwt_payload = {
                "user_id": user_data.get("id"),
                "email": user_data.get("email"),
                "name": user_data.get("name"),
                "picture": user_data.get("picture"),
                "exp": int(time.time()) + 3600  # 1 hour expiration
            }
            
            jwt_token = jwt.encode(jwt_payload, os.getenv("JWT_SECRET"), algorithm="HS256")
            
            # Redirect to frontend with token
            frontend_url = "http://localhost:5173"
            return RedirectResponse(url=f"{frontend_url}?token={jwt_token}")
            
    except Exception as e:
        print(f"OAuth callback error: {e}")
        raise HTTPException(status_code=400, detail="OAuth authentication failed")

@router.post("/google/one-tap")
async def google_one_tap(request: Request, one_tap_request: OneTapRequest):
    """Handle Google One-Tap authentication"""
    try:
        # Verify the Google ID token
        async with httpx.AsyncClient() as client:
            # Verify the token with Google
            verify_response = await client.get(
                f"https://oauth2.googleapis.com/tokeninfo?id_token={one_tap_request.credential}"
            )
            
            if verify_response.status_code != 200:
                raise HTTPException(status_code=400, detail="Invalid Google token")
            
            token_info = verify_response.json()
            
            # Create JWT token for our application
            jwt_payload = {
                "user_id": token_info.get("sub"),
                "email": token_info.get("email"),
                "name": token_info.get("name"),
                "picture": token_info.get("picture"),
                "exp": int(time.time()) + 3600  # 1 hour expiration
            }
            
            jwt_token = jwt.encode(jwt_payload, os.getenv("JWT_SECRET"), algorithm="HS256")
            
            return {"token": jwt_token, "user": jwt_payload}
            
    except Exception as e:
        print(f"One-tap authentication error: {e}")
        raise HTTPException(status_code=400, detail="One-tap authentication failed")

@router.get("/verify")
async def verify_token(token: str):
    """Verify JWT token and return user info."""
    try:
        payload = jwt.decode(token, os.getenv("JWT_SECRET"), algorithms=["HS256"])
        return {"valid": True, "user": payload}
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

@router.get("/user")
async def get_user_info(current_user: dict = Depends(get_current_user)):
    """Get current user information."""
    return current_user
