import os
from datetime import UTC, datetime, timedelta
from typing import Optional

from bson import ObjectId
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt

# --- Configuration ---
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60
USERS_COLLECTION = os.getenv("USERS_COLLECTION", "users")

# --- FastAPI Dependency ---
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/google/login")


# --- Helper Function for Creating Tokens ---
def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(UTC) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})

    if not JWT_SECRET_KEY:
        raise RuntimeError("JWT_SECRET_KEY is not configured in the environment.")

    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


# --- The Main Dependency for Protecting Routes ---
async def get_current_user(request: Request, token: str = Depends(oauth2_scheme)) -> dict:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if not JWT_SECRET_KEY:
        raise HTTPException(status_code=500, detail="Server authentication is not configured.")

    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str | None = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError as e:
        raise credentials_exception from e

    db = request.app.state.db
    user = await db[USERS_COLLECTION].find_one({"_id": ObjectId(user_id)})

    if user is None:
        raise credentials_exception

    return user

async def verify_jwt_token(token: str) -> Optional[str]:
    """
    Verify JWT token and return userId if valid.
    Used for WebSocket authentication where we can't use FastAPI dependencies.
    
    Args:
        token: JWT token string
        
    Returns:
        User ID string if valid, None otherwise
    """
    if not token or not JWT_SECRET_KEY:
        return None
    
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str | None = payload.get("sub")
        return user_id
    except JWTError:
        return None
    except Exception:
        return None