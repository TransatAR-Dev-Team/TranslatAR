import asyncio
import io
import logging
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, File, HTTPException, UploadFile
from faster_whisper import WhisperModel

# --- Logging Configuration ---
logging.basicConfig(level=logging.INFO, format="%(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

MODEL_SIZE = "base"

DEVICE = os.getenv("STT_DEVICE", "cpu")
COMPUTE_TYPE = "int8" if DEVICE == "cpu" else "auto"

ml_models = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Application startup...")
    logger.info("Loading Whisper model '%s' onto '%s' device...", MODEL_SIZE, DEVICE)
    try:
        ml_models["whisper_model"] = WhisperModel(
            MODEL_SIZE, device=DEVICE, compute_type=COMPUTE_TYPE
        )
        logger.info("Whisper model loaded successfully.")
    except Exception as e:
        logger.critical("CRITICAL: Failed to load Whisper model: %s", e, exc_info=True)
    yield
    logger.info("Application shutdown...")
    ml_models.clear()
    logger.info("Whisper model unloaded.")


app = FastAPI(lifespan=lifespan)


@app.post("/transcribe")
async def transcribe_audio(audio_file: UploadFile = File(...)):  # noqa: B008
    """
    Transcribes audio from an uploaded file using a pre-loaded Whisper model.

    Args:
        - audio_file (UploadFile): The audio file to be transcribed. This is expected to be
        - an instance of FastAPI's UploadFile, which allows for asynchronous file handling.

    Raises:
        - HTTPException:
            - 503: If the Whisper model is not loaded or ready.
            - 500: If an error occurs during the transcription process.
    Returns:
        - dict: A dictionary containing:
            - 'transcription': the transcribed text
            - 'detected_language': the ISO language code detected by Whisper
            - 'language_probability': confidence score for the detected language
    """

    if "whisper_model" not in ml_models:
        logger.error("Transcription request failed because the model is not loaded.")
        raise HTTPException(status_code=503, detail="Model is not loaded or ready.")

    logger.info("Received audio file '%s' for transcription.", audio_file.filename)
    try:
        audio_bytes = await audio_file.read()
        audio_stream = io.BytesIO(audio_bytes)

        loop = asyncio.get_event_loop()
        segments, info = await loop.run_in_executor(
            None,
            lambda: ml_models["whisper_model"].transcribe(audio_stream, vad_filter=True),
        )

        detected_language = info.language
        language_probability = info.language_probability

        logger.info(
            "Detected language '%s' with probability %f",
            detected_language,
            language_probability,
        )

        transcription_parts = [segment.text for segment in segments if segment.no_speech_prob < 0.6]
        transcription = "".join(transcription_parts).strip()

        logger.info(
            "Successfully transcribed audio. Result length: %d chars.",
            len(transcription),
        )
        
        return {
            "transcription": transcription,
            "detected_language": detected_language,
            "language_probability": language_probability,
        }

    except Exception as e:
        logger.error("Error during transcription: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail=f"An error occurred: {e}") from e


@app.get("/health")
def health_check():
    """Simple health check endpoint."""
    model_loaded = "whisper_model" in ml_models
    return {"status": "ok", "model_loaded": model_loaded}
