import os
import time
import jwt
import httpx
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel

router = APIRouter()

class OneTapRequest(BaseModel):
    credential: str

@router.get("/google")
async def google_login():
    """Initiate Google OAuth login"""
    client_id = os.getenv("GOOGLE_CLIENT_ID")
    redirect_uri = os.getenv("GOOGLE_REDIRECT_URI")
    
    if not client_id or not redirect_uri:
        raise HTTPException(status_code=500, detail="Google OAuth not configured")
    
    auth_url = (
        f"https://accounts.google.com/o/oauth2/v2/auth?"
        f"client_id={client_id}&"
        f"redirect_uri={redirect_uri}&"
        f"scope=openid email profile&"
        f"response_type=code&"
        f"access_type=offline"
    )
    
    return {"auth_url": auth_url}

@router.get("/google/callback")
async def google_callback(request: Request, code: str = None, error: str = None):
    """Handle Google OAuth callback"""
    if error:
        raise HTTPException(status_code=400, detail=f"OAuth error: {error}")
    
    if not code:
        raise HTTPException(status_code=400, detail="No authorization code provided")
    
    try:
        # Exchange code for token
        async with httpx.AsyncClient() as client:
            token_response = await client.post(
                "https://oauth2.googleapis.com/token",
                data={
                    "client_id": os.getenv("GOOGLE_CLIENT_ID"),
                    "client_secret": os.getenv("GOOGLE_CLIENT_SECRET"),
                    "code": code,
                    "grant_type": "authorization_code",
                    "redirect_uri": os.getenv("GOOGLE_REDIRECT_URI")
                }
            )
            
            if not token_response.is_success:
                raise HTTPException(status_code=400, detail="Failed to exchange code for token")
            
            token_data = token_response.json()
            access_token = token_data.get("access_token")
            
            if not access_token:
                raise HTTPException(status_code=400, detail="No access token received")
            
            # Get user info
            user_response = await client.get(
                "https://www.googleapis.com/oauth2/v2/userinfo",
                headers={"Authorization": f"Bearer {access_token}"}
            )
            
            if not user_response.is_success:
                raise HTTPException(status_code=400, detail="Failed to get user info")
            
            user_info = user_response.json()
            
            # Save user to database
            db = getattr(request.app.state, 'db', None)
            if not db:
                raise HTTPException(status_code=500, detail="Database not available")
            
            user = db.create_or_update_user({
                "email": user_info.get("email"),
                "name": user_info.get("name", ""),
                "picture": user_info.get("picture", ""),
                "sub": user_info.get("id")
            })
            
            # Create JWT token
            payload = {
                "user_id": str(user["_id"]),
                "email": user_info.get("email"),
                "name": user_info.get("name", ""),
                "exp": time.time() + 86400  # 24 hours
            }
            token = jwt.encode(payload, os.getenv("JWT_SECRET"), algorithm="HS256")
            
            # Return token and user info
            return {
                "jwt": token,
                "user": {
                    "id": str(user["_id"]),
                    "email": user_info.get("email"),
                    "name": user_info.get("name", ""),
                    "picture": user_info.get("picture", "")
                }
            }
            
    except Exception as e:
        print(f"OAuth callback error: {e}")
        raise HTTPException(status_code=400, detail="OAuth callback failed")

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
            
            if not verify_response.is_success:
                raise HTTPException(status_code=400, detail="Invalid Google token")
            
            token_info = verify_response.json()
            
            # Extract user information
            user_info = {
                "email": token_info.get("email"),
                "name": token_info.get("name", ""),
                "picture": token_info.get("picture", ""),
                "sub": token_info.get("sub")  # Google user ID
            }
            
            if not user_info["email"]:
                raise HTTPException(status_code=400, detail="No email in Google token")

            # Save user to database
            db = getattr(request.app.state, 'db', None)
            if not db:
                raise HTTPException(status_code=500, detail="Database not available")
            
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

    except Exception as e:
        print(f"One-tap authentication error: {e}")
        raise HTTPException(status_code=400, detail="One-tap authentication failed")

@router.get("/verify")
async def verify_token(request: Request, token: str):
    """Verify JWT token and return user info"""
    try:
        payload = jwt.decode(token, os.getenv("JWT_SECRET"), algorithms=["HS256"])
        user_id = payload.get("user_id")
        
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        # Get user from database
        db = getattr(request.app.state, 'db', None)
        if not db:
            raise HTTPException(status_code=500, detail="Database not available")
        
        user = db.get_user_by_id(user_id)
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        return {
            "valid": True,
            "user": {
                "id": str(user["_id"]),
                "email": user.get("email"),
                "name": user.get("name", ""),
                "picture": user.get("picture", "")
            }
        }
        
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")
    except Exception as e:
        print(f"Token verification error: {e}")
        raise HTTPException(status_code=500, detail="Token verification failed")
