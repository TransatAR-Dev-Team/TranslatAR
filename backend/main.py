import os
import httpx
from fastapi import FastAPI, APIRouter, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import motor.motor_asyncio
from pydantic import BaseModel

STT_SERVICE_URL = os.getenv("STT_URL", "http://stt:9000")
TRANSLATION_SERVICE_URL = os.getenv("TRANSLATION_URL", "http://translation:9001")

app = FastAPI()
router = APIRouter()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class TranslationResponse(BaseModel):
    original_text: str
    translated_text: str

@router.get("/data")
def read_data():
    return {"message": "Hello from the FastAPI backend!"}

client = motor.motor_asyncio.AsyncIOMotorClient("mongodb://mongodb:27017")
database = client.helloworld_db
message_collection = database.get_collection("messages")

@router.get("/db-hello")
async def read_db_hello():
    greeting = await message_collection.find_one({"type": "greeting"})
    if not greeting:
        await message_collection.insert_one(
            {"type": "greeting", "message": "Hello from MongoDB!"}
        )
        greeting = await message_collection.find_one({"type": "greeting"})
    return {"message": greeting["message"]}


@router.post("/process-audio", response_model=TranslationResponse)
async def process_audio_and_translate(
    audio_file: UploadFile = File(...),
    source_lang: str = Form("en"),
    target_lang: str = Form("es")
):
    """
    Receives an audio file, sends it for transcription, then translates the result.
    """
    async with httpx.AsyncClient(timeout=60.0) as client:
        try:
            # --- Step 1: Send audio to STT service ---
            stt_files = {'audio_file': (audio_file.filename, await audio_file.read(), audio_file.content_type)}
            stt_response = await client.post(f"{STT_SERVICE_URL}/transcribe", files=stt_files)
            stt_response.raise_for_status()
            
            transcribed_data = stt_response.json()
            original_text = transcribed_data.get("transcription")

            if not original_text:
                raise HTTPException(status_code=500, detail="Transcription failed or returned empty text.")

        except httpx.RequestError as e:
            raise HTTPException(status_code=503, detail=f"Could not connect to the STT service: {e}")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"An error occurred during transcription: {str(e)}")

        try:
            # --- Step 2: Send transcribed text to Translation service ---
            translation_payload = {
                "text": original_text,
                "source_lang": source_lang,
                "target_lang": target_lang
            }
            translation_response = await client.post(f"{TRANSLATION_SERVICE_URL}/translate", json=translation_payload)
            translation_response.raise_for_status()

            translated_data = translation_response.json()
            translated_text = translated_data.get("translated_text")

            if translated_text is None:
                raise HTTPException(status_code=500, detail="Translation failed or returned empty text.")

        except httpx.RequestError as e:
            raise HTTPException(status_code=503, detail=f"Could not connect to the translation service: {e}")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"An error occurred during translation: {str(e)}")

        # --- Step 3: Return the final result ---
        return TranslationResponse(
            original_text=original_text,
            translated_text=translated_text
        )

app.include_router(router, prefix="/api")
