# ruff: noqa: B008

import os
import uuid
from datetime import UTC, datetime

import httpx
import motor.motor_asyncio
from fastapi import APIRouter, FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pymongo.errors import ConnectionFailure

from websocket import router as websocket_router

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

# --- WebSocket Router ---
app.include_router(websocket_router)

# --- Database Connection ---
client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_DATABASE_URL)
db = client.translatar_db
translations_collection = db.get_collection("translations")
settings_collection = db.get_collection("settings")


# --- Pydantic Models ---
class TranslationResponse(BaseModel):
    original_text: str
    translated_text: str
    conversation_id: str


class SummarizationRequest(BaseModel):
    text: str
    length: str = "medium"


class SummarizationResponse(BaseModel):
    summary: str


class SettingsModel(BaseModel):
    source_language: str = "en"
    target_language: str = "es"
    chunk_duration_seconds: float = 8.0
    target_sample_rate: int = 48000
    silence_threshold: float = 0.01
    chunk_overlap_seconds: float = 0.5
    websocket_url: str = "ws://localhost:8000/ws"


class SettingsResponse(BaseModel):
    settings: SettingsModel


# --- Endpoints ---


@router.get("/db-hello")
async def read_db_hello():
    hello_db = client.helloworld_db
    hello_coll = hello_db.get_collection("messages")
    greeting = await hello_coll.find_one({"type": "greeting"})
    if not greeting:
        await hello_coll.insert_one({"type": "greeting", "message": "Hello from MongoDB!"})
        greeting = await hello_coll.find_one({"type": "greeting"})
    return {"message": greeting["message"]}


@router.post("/process-audio", response_model=TranslationResponse)
async def process_audio_and_translate(
    audio_file: UploadFile = File(...),
    source_lang: str = Form("en"),
    target_lang: str = Form("es"),
    conversation_id: str = Form(None),
    username: str = Form(None)
):
    if conversation_id is "":
        conversation_id = str(uuid.uuid4()) 
    if username is "":
        username = "anonymous"
    async with httpx.AsyncClient(timeout=60.0) as client:
        # Step 1: STT call
        try:
            stt_files = {
                "audio_file": (
                    audio_file.filename,
                    await audio_file.read(),
                    audio_file.content_type,
                )
            }
            stt_response = await client.post(f"{STT_SERVICE_URL}/transcribe", files=stt_files)
            stt_response.raise_for_status()
            original_text = stt_response.json().get("transcription")
            if not original_text:
                raise HTTPException(status_code=500, detail="Transcription failed.")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error in STT service: {e}") from e

        # Step 2: Translation call
        try:
            translation_payload = {
                "text": original_text,
                "source_lang": source_lang,
                "target_lang": target_lang,
            }
            translation_response = await client.post(
                f"{TRANSLATION_SERVICE_URL}/translate", json=translation_payload
            )
            translation_response.raise_for_status()
            translated_text = translation_response.json().get("translated_text")
            if translated_text is None:
                raise HTTPException(status_code=500, detail="Translation failed.")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error in Translation service: {e}") from e

        # Step 3: Save to the DB
        try:
            translation_log = {
                "conversation_id": conversation_id,
                "username": username,
                "original_text": original_text,
                "translated_text": translated_text,
                "source_lang": source_lang,
                "target_lang": target_lang,
                "timestamp": datetime.now(UTC),
            }
            await translations_collection.insert_one(translation_log)
        except Exception as e:
            print(f"CRITICAL: Failed to save translation to database: {e}")

        return TranslationResponse(
            original_text=original_text,
            translated_text=translated_text,
            conversation_id=conversation_id
        )
    
@router.get("/history/{username}")
async def get_history(username: str | None = None, conversation_id: str | None = None):
    """
    Retrieves the translation records from the database.
    """
    try:
        query = {"username":username}
        
        if conversation_id:
            query["conversation_id"] = conversation_id
        
        
        history_cursor = (
            translations_collection.find(query)
            .sort("timestamp", -1)
            .limit(50)
        )
        history_list = []
        async for doc in history_cursor:
            doc["_id"] = str(doc["_id"])
            history_list.append(doc)

        return {"history": history_list}
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to retrieve history from database: {e}"
        ) from e


@router.post("/summarize", response_model=SummarizationResponse)
async def get_summary(request: SummarizationRequest):
    """
    Receives text and a desired length, then forwards to the summarization service.
    """
    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            payload = {"text": request.text, "length": request.length}
            response = await client.post(f"{SUMMARIZATION_SERVICE_URL}/summarize", json=payload)
            response.raise_for_status()
            summary_text = response.json().get("summary")
            if summary_text is None:
                raise HTTPException(status_code=500, detail="Summarization failed.")
            return SummarizationResponse(summary=summary_text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error during summarization: {e}") from e


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
        # The 'ping' command is cheap and does not require auth.
        await client.admin.command("ping")
        return {"status": "ok", "database_status": "connected"}
    except ConnectionFailure as e:
        raise HTTPException(
            status_code=503,
            detail=f"Service Unavailable: Cannot connect to the database. Error: {e}",
        ) from e


app.include_router(router, prefix="/api")
