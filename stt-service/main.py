from fastapi import FastAPI, UploadFile, File, HTTPException
from faster_whisper import WhisperModel
import asyncio
from contextlib import asynccontextmanager
import logging
import os
import io

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

MODEL_SIZE = "base"

DEVICE = os.getenv("STT_DEVICE", "cpu")

if DEVICE == "cuda":
    COMPUTE_TYPE = "auto"
    logger.info("Configured for GPU (CUDA) execution.")
else:
    COMPUTE_TYPE = "int8"
    logger.info("Configured for CPU execution.")

ml_models = {}

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(f"Loading Whisper model '{MODEL_SIZE}' onto '{DEVICE}' device...")
    ml_models["whisper_model"] = WhisperModel(
        MODEL_SIZE, 
        device=DEVICE, 
        compute_type=COMPUTE_TYPE
    )
    logger.info("Whisper model loaded successfully.")
    yield
    ml_models.clear()
    logger.info("Whisper model unloaded.")

app = FastAPI(lifespan=lifespan)

@app.post("/transcribe")
async def transcribe_audio(audio_file: UploadFile = File(...)):
    """
    Accepts an audio file and returns the transcription.
    """
    if "whisper_model" not in ml_models:
        raise HTTPException(status_code=503, detail="Model is not loaded or ready.")

    try:
        audio_bytes = await audio_file.read()
        audio_stream = io.BytesIO(audio_bytes)

        loop = asyncio.get_event_loop()
        segments, info = await loop.run_in_executor(
            None,
            lambda: ml_models["whisper_model"].transcribe(audio_stream)
        )

        logger.info(f"Detected language '{info.language}' with probability {info.language_probability}")
        transcription = "".join(segment.text for segment in segments)
        
        return {"transcription": transcription.strip()}

    except Exception as e:
        logger.error(f"Error during transcription: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
def health_check():
    """Simple health check endpoint."""
    return {"status": "ok", "model_loaded": "whisper_model" in ml_models}
