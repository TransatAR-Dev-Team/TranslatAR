import logging

from fastapi import APIRouter, HTTPException, Request

from models.settings import SettingsModel, SettingsResponse

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("", response_model=SettingsResponse)
async def get_settings(request: Request):
    """
    Retrieves the current application settings from the database.
    If no settings exist, returns default values.
    """
    logger.info("Attempting to retrieve settings from database.")
    try:
        settings_collection = request.app.state.db.get_collection("settings")
        settings_doc = await settings_collection.find_one({})

        if not settings_doc:
            logger.info("No settings found in database, returning default values.")
            default_settings = SettingsModel()
            return SettingsResponse(settings=default_settings)
        else:
            logger.info("Successfully retrieved settings from database.")
            # Remove MongoDB _id field before returning
            settings_doc.pop("_id", None)
            settings = SettingsModel(**settings_doc)
            return SettingsResponse(settings=settings)

    except Exception as e:
        logger.error("Failed to retrieve settings from database: %s", e, exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve settings from database: {e}",
        ) from e


@router.post("", response_model=SettingsResponse)
async def save_settings(request: Request, settings_update: SettingsModel):
    """
    Saves or updates application settings in the database.
    """
    logger.info("Attempting to save settings to database.")
    try:
        settings_collection = request.app.state.db.get_collection("settings")
        # Convert to dict for MongoDB insertion
        settings_dict = settings_update.model_dump()

        # Upsert the settings (insert if doesn't exist, update if exists)
        await settings_collection.replace_one(
            {},  # empty filter matches any document (there's only one settings document)
            settings_dict,
            upsert=True,
        )
        logger.info("Successfully saved settings to database.")
        return SettingsResponse(settings=settings_update)

    except Exception as e:
        logger.error("Failed to save settings to database: %s", e, exc_info=True)
        raise HTTPException(
            status_code=500, detail=f"Failed to save settings to database: {e}"
        ) from e
