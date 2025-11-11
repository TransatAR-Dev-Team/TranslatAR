# ruff: noqa: B008

import os
from datetime import UTC, datetime

import httpx
from fastapi import APIRouter, File, Form, HTTPException, Request, UploadFile

from models.translation import TranslationResponse

# --- Configuration ---
STT_SERVICE_URL = os.getenv("STT_URL", "http://stt:9000")
TRANSLATION_SERVICE_URL = os.getenv("TRANSLATION_URL", "http://translation:9001")
SUMMARIZATION_SERVICE_URL = os.getenv("SUMMARIZATION_URL", "http://summarization:9002")

router = APIRouter()


@router.post("", response_model=TranslationResponse)
async def process_audio_and_translate(
    request: Request,
    audio_file: UploadFile = File(...),
    source_lang: str = Form("en"),
    target_lang: str = Form("es"),
):
    translations_collection = request.app.state.db.get_collection("translations")

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
                "original_text": original_text,
                "translated_text": translated_text,
                "source_lang": source_lang,
                "target_lang": target_lang,
                "timestamp": datetime.now(UTC),
            }
            await translations_collection.insert_one(translation_log)
        except Exception as e:
            print(f"CRITICAL: Failed to save translation to database: {e}")

        return TranslationResponse(original_text=original_text, translated_text=translated_text)
