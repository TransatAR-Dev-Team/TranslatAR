import logging

from fastapi import APIRouter, Depends, HTTPException, Request

from models.settings import SettingsModel, SettingsResponse
from security.auth import get_current_user

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("", response_model=SettingsResponse)
async def get_settings(
    request: Request, current_user: dict = Depends(get_current_user)  # noqa: B008
):
    """
    Retrieves the current application settings from the database for the authenticated user.
    If no settings exist for the user, returns default values.
    """
    user_id = str(current_user["_id"])
    logger.info(f"Attempting to retrieve settings from database for user: {user_id}")
    try:
        settings_collection = request.app.state.db.get_collection("settings")
        settings_doc = await settings_collection.find_one({"userId": user_id})

        if not settings_doc:
            logger.info(f"No settings found for user {user_id}, returning default values.")
            default_settings = SettingsModel()
            return SettingsResponse(settings=default_settings)
        else:
            logger.info(f"Successfully retrieved settings for user {user_id}.")
            settings_doc.pop("_id", None)
            settings_doc.pop("userId", None)
            settings = SettingsModel(**settings_doc)
            return SettingsResponse(settings=settings)

    except Exception as e:
        logger.error(f"Failed to retrieve settings for user {user_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to retrieve settings: {e}") from e


@router.post("", response_model=SettingsResponse)
async def save_settings(
    request: Request,
    settings_update: SettingsModel,
    current_user: dict = Depends(get_current_user),  # noqa: B008
):
    """
    Saves or updates application settings for the authenticated user in the database.
    """
    user_id = str(current_user["_id"])
    logger.info(f"Attempting to save settings to database for user: {user_id}")

    try:
        settings_collection = request.app.state.db.get_collection("settings")
        settings_dict = settings_update.model_dump()

        settings_dict["userId"] = user_id

        await settings_collection.replace_one(
            {"userId": user_id},
            settings_dict,
            upsert=True,
        )
        logger.info(f"Successfully saved settings for user {user_id}.")
        return SettingsResponse(settings=settings_update)

    except Exception as e:
        logger.error(f"Failed to save settings for user {user_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to save settings: {e}") from e
