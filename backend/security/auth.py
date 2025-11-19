import logging
import os
from datetime import UTC, datetime, timedelta
from typing import Optional

from bson import ObjectId
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt

logger = logging.getLogger(__name__)

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
        logger.critical(
            "CRITICAL: JWT_SECRET_KEY is not configured. Did you read the set up instructions?"
        )
        raise RuntimeError("JWT_SECRET_KEY is not configured in the environment.")

    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=ALGORITHM)
    logger.info("Created new access token for subject: %s", data.get("sub"))
    return encoded_jwt


# --- The Main Dependency for Protecting Routes ---
async def get_current_user(request: Request, token: str = Depends(oauth2_scheme)) -> dict:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if not JWT_SECRET_KEY:
        logger.critical("CRITICAL: JWT_SECRET_KEY is not configured. Cannot validate tokens.")
        raise HTTPException(status_code=500, detail="Server authentication is not configured.")

    try:
        logger.info("Attempting to decode access token.")
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str | None = payload.get("sub")
        if user_id is None:
            logger.warning("Token decoding failed: 'sub' claim missing from payload.")
            raise credentials_exception
        logger.info("Token successfully decoded for user_id: %s", user_id)
    except JWTError as e:
        # This is often a client-side issue (e.g., expired token), so a warning is suitable.
        logger.warning("JWT Error during token decoding: %s", e)
        raise credentials_exception from e

    db = request.app.state.db
    logger.info("Fetching user from database with user_id: %s", user_id)
    user = await db[USERS_COLLECTION].find_one({"_id": ObjectId(user_id)})

    if user is None:
        # A valid token for a non-existent user could be a security concern or a data issue.
        logger.warning("User with ID %s from a valid token was not found in the database.", user_id)
        raise credentials_exception

    logger.info("Successfully authenticated user: %s", user.get("email"))
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