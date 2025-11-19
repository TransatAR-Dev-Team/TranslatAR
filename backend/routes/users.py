import logging

from fastapi import APIRouter, Depends

from models.user import UserModel
from security.auth import get_current_user

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/me", response_model=UserModel)
async def read_users_me(current_user: dict = Depends(get_current_user)):  # noqa: B008
    """
    Get the details for the currently authenticated user.
    """
    user_email = current_user.get("email", "unknown")
    logger.info("Successfully retrieved profile for authenticated user: %s", user_email)
    # The 'get_current_user' dependency already fetches the user document from the DB.
    # We just need to return it. Pydantic will handle the serialization.
    return current_user
