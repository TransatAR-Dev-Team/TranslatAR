import logging
import os

from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config.database import db
from routes.auth import router as auth_router
from routes.auth_unity import router as auth_unity_router
from routes.genadvice import router as advice_router
from routes.health import router as health_router
from routes.history import router as history_router
from routes.process_audio import router as process_audio_router
from routes.settings import router as settings_router
from routes.summarization import router as summarization_router
from routes.users import router as users_router
from routes.websocket import router as websocket_router

# --- Logging Configuration ---
logging.basicConfig(level=logging.INFO, format="%(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# --- Configuration ---
STT_SERVICE_URL = os.getenv("STT_URL", "http://stt:9000")
TRANSLATION_SERVICE_URL = os.getenv("TRANSLATION_URL", "http://translation:9001")
SUMMARIZATION_SERVICE_URL = os.getenv("SUMMARIZATION_URL", "http://summarization:9002")
ADVICE_SERVICE_URL = os.getenv("ADVICE_URL", "http://advice:9003")
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
router.include_router(health_router, prefix="/health", tags=["Health"])
router.include_router(auth_router, prefix="/auth", tags=["Authentication", "Web OAuth"])
router.include_router(
    auth_unity_router, prefix="/auth/device", tags=["Authentication", "Device OAuth"]
)
router.include_router(advice_router, prefix="/advice", tags=["Advice Generation"])
router.include_router(history_router, prefix="/history", tags=["History"])
router.include_router(process_audio_router, prefix="/process-audio", tags=["Audio Processing"])
router.include_router(settings_router, prefix="/settings", tags=["Settings"])
router.include_router(summarization_router, prefix="/summarize", tags=["Summarization"])
router.include_router(users_router, prefix="/users", tags=["Users"])
app.include_router(websocket_router, prefix="/ws", tags=["WebSocket"])


# --- Database Connection ---
translations_collection = db.get_collection("translations")
settings_collection = db.get_collection("settings")
app.state.db = db


app.include_router(router, prefix="/api")
