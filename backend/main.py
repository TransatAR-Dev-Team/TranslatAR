import os

from fastapi import APIRouter, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pymongo.errors import ConnectionFailure

from config.database import client, db
from models.settings import SettingsModel, SettingsResponse
from routes.auth import router as auth_router
from routes.auth_unity import router as auth_unity_router
from routes.history import router as history_router
from routes.process_audio import router as process_audio_router
from routes.summarization import router as summarization_router
from routes.users import router as users_router
from routes.websocket import router as websocket_router

# --- Configuration ---
STT_SERVICE_URL = os.getenv("STT_URL", "http://stt:9000")
TRANSLATION_SERVICE_URL = os.getenv("TRANSLATION_URL", "http://translation:9001")
SUMMARIZATION_SERVICE_URL = os.getenv("SUMMARIZATION_URL", "http://summarization:9002")

MONGO_DATABASE_URL = os.getenv("DATABASE_URL", "mongodb://mongodb:27017")

# --- FastAPI App & Router Setup ---
app = FastAPI()
router = APIRouter()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Include Routers ---
router.include_router(auth_router, prefix="/auth", tags=["Authentication", "Web OAuth"])
router.include_router(
    auth_unity_router, prefix="/auth/device", tags=["Authentication", "Device OAuth"]
)
router.include_router(history_router, prefix="/history", tags=["History"])
router.include_router(process_audio_router, prefix="/process-audio", tags=["Audio Processing"])
router.include_router(summarization_router, prefix="/summarize", tags=["Summarization"])
router.include_router(users_router, prefix="/users", tags=["Users"])
app.include_router(websocket_router, prefix="/ws", tags=["WebSocket"])

# --- Database Connection ---
translations_collection = db.get_collection("translations")
settings_collection = db.get_collection("settings")
app.state.db = db


# --- Endpoints ---
@router.get("/settings", response_model=SettingsResponse)
async def get_settings():
    """
    Retrieves the current application settings from the database.
    If no settings exist, returns default values.
    """
    try:
        settings_doc = await settings_collection.find_one({})

        if not settings_doc:
            # Return default settings if none exist
            default_settings = SettingsModel()
            return SettingsResponse(settings=default_settings)
        else:
            # Remove MongoDB _id field before returning
            settings_doc.pop("_id", None)
            settings = SettingsModel(**settings_doc)
            return SettingsResponse(settings=settings)

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve settings from database: {e}",
        ) from e


@router.post("/settings", response_model=SettingsResponse)
async def save_settings(settings_update: SettingsModel):
    """
    Saves or updates application settings in the database.
    """
    try:
        # Convert to dict for MongoDB insertion
        settings_dict = settings_update.model_dump()

        # Upsert the settings (insert if doesn't exist, update if exists)
        await settings_collection.replace_one(
            {},  # empty filter matches any document (there's only one settings document)
            settings_dict,
            upsert=True,
        )

        return SettingsResponse(settings=settings_update)

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to save settings to database: {e}"
        ) from e


@router.get("/health")
async def health_check():
    """
    Checks the health of the service, including the database connection.
    """
    try:
        await client.admin.command("ping")
        return {"status": "ok", "database_status": "connected"}
    except ConnectionFailure as e:
        raise HTTPException(
            status_code=503,
            detail=f"Service Unavailable: Cannot connect to the database. Error: {e}",
        ) from e


app.include_router(router, prefix="/api")
