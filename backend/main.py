import os
import httpx
from fastapi import FastAPI, APIRouter, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import motor.motor_asyncio
from pydantic import BaseModel
from pymongo.errors import ConnectionFailure
from datetime import datetime, timezone
from dotenv import load_dotenv

from websocket import router as websocket_router
from auth_controller import router as auth_router
from database_client import DatabaseClient

load_dotenv()

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

# --- Auth Router (with /api prefix) ---
app.include_router(auth_router, prefix="/api/auth")

# --- Database Connection ---
client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_DATABASE_URL)
db = client.translatar_db
translations_collection = db.get_collection("translations")
settings_collection = db.get_collection("settings")

# --- Startup Event: Initialize Database Client for Auth ---
@app.on_event("startup")
async def startup_event():
    """Initialize database client (async Motor)"""
    db_client = DatabaseClient(MONGO_DATABASE_URL)
    app.state.db = db_client
    print("Database client initialized for authentication")

@app.on_event("shutdown")
async def shutdown_event():
    """Close database connection"""
    if hasattr(app.state, 'db'):
        app.state.db.client.close()
        print("Database client closed")

# --- Initialize Database Client for compatibility ---
# This is set for routes that don't use the startup event
# The startup event will override this
db_client = DatabaseClient(MONGO_DATABASE_URL)
app.state.db = db_client

# --- Pydantic Models ---
class TranslationResponse(BaseModel):
    original_text: str
    translated_text: str

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
        await hello_coll.insert_one(
            {"type": "greeting", "message": "Hello from MongoDB!"}
        )
        greeting = await hello_coll.find_one({"type": "greeting"})
    return {"message": greeting["message"]}


@router.post("/process-audio", response_model=TranslationResponse)
async def process_audio_and_translate(
    audio_file: UploadFile = File(...),
    source_lang: str = Form("en"),
    target_lang: str = Form("es")
):
    async with httpx.AsyncClient(timeout=60.0) as client:
        # Step 1: STT call
        try:
            stt_files = {'audio_file': (audio_file.filename, await audio_file.read(), audio_file.content_type)}
            stt_response = await client.post(f"{STT_SERVICE_URL}/transcribe", files=stt_files)
            stt_response.raise_for_status()
            original_text = stt_response.json().get("transcription")
            if not original_text:
                raise HTTPException(status_code=500, detail="Transcription failed.")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error in STT service: {str(e)}")

        # Step 2: Translation call
        try:
            translation_payload = {"text": original_text, "source_lang": source_lang, "target_lang": target_lang}
            translation_response = await client.post(f"{TRANSLATION_SERVICE_URL}/translate", json=translation_payload)
            translation_response.raise_for_status()
            translated_text = translation_response.json().get("translated_text")
            if translated_text is None:
                raise HTTPException(status_code=500, detail="Translation failed.")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error in Translation service: {str(e)}")


        # Step 3: Save to the DB
        try:
            translation_log = {
                "original_text": original_text,
                "translated_text": translated_text,
                "source_lang": source_lang,
                "target_lang": target_lang,
                "timestamp": datetime.now(timezone.utc)
            }
            await translations_collection.insert_one(translation_log)
        except Exception as e:
            print(f"CRITICAL: Failed to save translation to database: {e}")

        return TranslationResponse(
            original_text=original_text,
            translated_text=translated_text
        )
    
@router.get("/history")
async def get_history():
    """
    Retrieves the translation records from the database.
    """
    try:
        history_cursor = translations_collection.find({}).sort("timestamp", -1).limit(50)
        
        history_list = []
        async for doc in history_cursor:
            doc["_id"] = str(doc["_id"])
            history_list.append(doc)
            
        return {"history": history_list}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve history from database: {str(e)}")

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
        raise HTTPException(status_code=500, detail=f"Error during summarization: {str(e)}")

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
        raise HTTPException(status_code=500, detail=f"Failed to retrieve settings from database: {str(e)}")

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
            upsert=True
        )

        return SettingsResponse(settings=settings_update)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save settings to database: {str(e)}")

@router.get("/health")
async def health_check():
    """
    Checks the health of the service, including the database connection.
    """
    try:
        # The 'ping' command is cheap and does not require auth.
        await client.admin.command('ping')
        return {"status": "ok", "database_status": "connected"}
    except ConnectionFailure as e:
        raise HTTPException(
            status_code=503, 
            detail=f"Service Unavailable: Cannot connect to the database. Error: {e}"
        )

app.include_router(router, prefix="/api")

# --- Static Files (for login page) ---
# Mount static files AFTER all routers to avoid conflicts
import pathlib
static_dir = pathlib.Path(__file__).parent / "static"
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")
