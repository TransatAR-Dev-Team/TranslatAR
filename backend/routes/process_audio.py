# ruff: noqa: B008

import logging
import os
from datetime import UTC, datetime

import httpx
from fastapi import APIRouter, File, Form, HTTPException, Request, UploadFile, Depends
from security.auth import get_current_user

from models.translation import TranslationResponse

# --- Configuration ---
STT_SERVICE_URL = os.getenv("STT_URL", "http://stt:9000")
TRANSLATION_SERVICE_URL = os.getenv("TRANSLATION_URL", "http://translation:9001")

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("", response_model=TranslationResponse)
async def process_audio_and_translate(
    request: Request,
    audio_file: UploadFile = File(...),
    source_lang: str = Form("en"),
    target_lang: str = Form("es"),
    current_user: dict = Depends(get_current_user),
):
    logger.info(
        "Processing audio for translation from '%s' to '%s'.",
        source_lang,
        target_lang,
    )
    translations_collection = request.app.state.db.get_collection("translations")

    async with httpx.AsyncClient(timeout=60.0) as client:
        # Step 1: STT call
        try:
            logger.info("Forwarding audio to STT service at %s", STT_SERVICE_URL)
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
                logger.warning("STT service returned an empty transcription.")
                raise HTTPException(
                    status_code=400, detail="Transcription failed (no speech detected)."
                )
            logger.info("Successfully transcribed text: '%s'", original_text)
        except Exception as e:
            logger.error("Error calling STT service: %s", e, exc_info=True)
            raise HTTPException(status_code=502, detail=f"Error in STT service: {e}") from e

        # Step 2: Translation call
        try:
            logger.info("Forwarding text to translation service at %s", TRANSLATION_SERVICE_URL)
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
                logger.error("Translation service did not return 'translated_text'.")
                raise HTTPException(status_code=500, detail="Translation failed.")
            logger.info("Successfully translated text: '%s'", translated_text)
        except Exception as e:
            logger.error("Error calling Translation service: %s", e, exc_info=True)
            raise HTTPException(status_code=502, detail=f"Error in Translation service: {e}") from e

        # Step 3: Save to the DB
        try:
            logger.info("Saving translation to the database.")
            translation_log = {
                "original_text": original_text,
                "translated_text": translated_text,
                "source_lang": source_lang,
                "target_lang": target_lang,
                "userId": str(current_user["_id"]),
                "timestamp": datetime.now(UTC),
            }
            await translations_collection.insert_one(translation_log)
            logger.info("Successfully saved translation to the database.")
        except Exception as e:
            logger.critical(
                "CRITICAL: Failed to save translation to database: %s", e, exc_info=True
            )

        return TranslationResponse(original_text=original_text, translated_text=translated_text)
