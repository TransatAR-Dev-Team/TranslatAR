"""
Google OAuth Authentication Controller (Client-Side Flow)
Reference: https://github.com/ekourtakis/RetroInsta

This implements a client-side OAuth flow where:
1. Frontend uses Google Identity Services to get an ID Token
2. Frontend sends ID Token to this backend endpoint
3. Backend verifies the ID Token with Google
4. Backend creates/updates user in database
5. Backend returns application's own JWT
"""
from fastapi import APIRouter, HTTPException, Request, Header
from typing import Optional
from pydantic import BaseModel
from security import JWTManager, GoogleIDTokenVerifier
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

# --- Request/Response Models ---
class GoogleLoginRequest(BaseModel):
    idToken: str

class GoogleLoginResponse(BaseModel):
    success: bool = True
    data: dict
    message: Optional[str] = None

class UserResponse(BaseModel):
    success: bool = True
    data: dict
    message: Optional[str] = None

class TokenVerifyResponse(BaseModel):
    success: bool = True
    data: dict
    message: Optional[str] = None


def get_current_user_from_header(authorization: str) -> dict:
    """
    Verify JWT token from Authorization header and return user info
    
    Args:
        authorization: Authorization header (format: Bearer <token>)
    
    Returns:
        Decoded user info
    """
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing Authorization header")
    
    # Extract Bearer token
    parts = authorization.split(" ")
    if len(parts) != 2 or parts[0] != "Bearer":
        raise HTTPException(status_code=401, detail="Invalid authorization header format")
    
    token = parts[1]
    return JWTManager.verify_token(token)


@router.post("/google/login", response_model=GoogleLoginResponse)
async def google_login(login_request: GoogleLoginRequest, http_request: Request):
    """
    Handle Google OAuth login (client-side flow)
    
    Frontend sends ID Token obtained from Google Identity Services
    Backend verifies token and creates/updates user
    Returns application's own JWT
    
    Request body: { "idToken": "..." }
    Returns: { "success": true, "data": { "token": "...", "user": {...} }, "message": null }
    """
    try:
        # Verify Google ID Token
        user_claims = await GoogleIDTokenVerifier.verify_id_token(login_request.idToken)
        
        # Extract user info
        google_id = user_claims.get("sub")  # Google's unique user ID
        email = user_claims.get("email", "")
        name = user_claims.get("name", "")
        picture = user_claims.get("picture", "")
        
        if not email:
            raise HTTPException(status_code=400, detail="Token missing email")
        
        # Get database client
        db = http_request.app.state.db
        
        # Find or create user
        user = await db.create_or_update_user({
            "google_id": google_id,
            "email": email,
            "name": name,
            "picture": picture
        })
        
        # Create application JWT
        app_token = JWTManager.create_token(
            user_id=str(user["_id"]),
            email=email,
            name=name
        )
        
        # Return standardized response
        return GoogleLoginResponse(
            success=True,
            data={
                "token": app_token,
                "user": {
                    "id": str(user["_id"]),
                    "email": email,
                    "name": name,
                    "picture": picture
                }
            },
            message=None
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {e}")
        raise HTTPException(status_code=500, detail=f"Login failed: {str(e)}")


@router.get("/verify", response_model=TokenVerifyResponse)
async def verify_token(authorization: str = Header(None)):
    """
    Verify JWT Token validity
    
    Headers:
        Authorization: Bearer <token>
    
    Returns: { "success": true, "data": { "valid": true, "decoded": {...} }, "message": null }
    """
    try:
        if not authorization:
            raise HTTPException(status_code=401, detail="Missing Authorization header")
        
        # Extract and verify token
        user_data = get_current_user_from_header(authorization)
        
        return TokenVerifyResponse(
            success=True,
            data={
                "valid": True,
                "decoded": user_data
            },
            message=None
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Token verification error: {e}")
        raise HTTPException(status_code=401, detail=f"Token verification failed: {str(e)}")


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(request: Request):
    """
    Get current user information (from JWT token)
    
    Headers:
        Authorization: Bearer <token>
    
    Returns: { "success": true, "data": { ...user info... }, "message": null }
    """
    try:
        # Extract authorization header
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            raise HTTPException(status_code=401, detail="Missing Authorization header")
        
        # Verify token
        user_data = get_current_user_from_header(auth_header)
        
        # Get full user info from database
        db = request.app.state.db
        user = await db.get_user_by_id(user_data["user_id"])
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Return standardized response
        return UserResponse(
            success=True,
            data={
                "id": str(user["_id"]),
                "email": user["email"],
                "name": user.get("name", ""),
                "picture": user.get("picture", ""),
                "settings": user.get("settings", {})
            },
            message=None
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting user info: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get user info: {str(e)}")
