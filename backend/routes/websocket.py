import asyncio
import json
import logging
import os
from datetime import UTC, datetime
from uuid import uuid4

import httpx
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from security.auth import verify_jwt_token

logger = logging.getLogger(__name__)

router = APIRouter()

# Service URLs from environment
STT_SERVICE_URL = os.getenv("STT_URL", "http://stt:9000")
TRANSLATION_SERVICE_URL = os.getenv("TRANSLATION_URL", "http://translation:9001")


@router.websocket("")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    client_host = websocket.client.host if websocket.client else "unknown"
    logger.info("WebSocket client connected from: %s", client_host)

    # Store userId for this connection
    user_id = None

    try:
        # First message should contain authentication
        first_data = await websocket.receive_bytes()
        metadata_length = int.from_bytes(first_data[:4], byteorder="little")
        metadata_json = first_data[4 : 4 + metadata_length].decode("utf-8")
        metadata = json.loads(metadata_json)

        # Authenticate the connection
        jwt_token = metadata.get("jwt_token")
        if jwt_token:
            user_id = await verify_jwt_token(jwt_token)
            if user_id:
                logger.info(f"WebSocket authenticated for user: {user_id}")
            else:
                logger.warning("JWT verification failed")
                await websocket.close(code=4001, reason="Authentication failed")
                return
        else:
            logger.warning("No JWT token provided in initial message")

        # Process first audio chunk
        audio_data = first_data[4 + metadata_length :]
        source_lang = metadata.get("source_lang", "en")
        target_lang = metadata.get("target_lang", "es")
        conversation_id = metadata.get("conversation_id")

        # Process sequentially - await this before accepting next message
        await process_audio_chunk(
            websocket, audio_data, source_lang, target_lang, user_id, conversation_id
        )

        # Continue receiving subsequent messages
        while True:
            data = await websocket.receive_bytes()
            metadata_length = int.from_bytes(data[:4], byteorder="little")
            metadata_json = data[4 : 4 + metadata_length].decode("utf-8")
            audio_data = data[4 + metadata_length :]
            metadata = json.loads(metadata_json)

            source_lang = metadata.get("source_lang", "en")
            target_lang = metadata.get("target_lang", "es")
            
            conversation_id = metadata.get("conversation_id", conversation_id)

            logger.info(
                "Received audio chunk from user %s: %d bytes, lang: %s -> %s",
                user_id or "NO USER ID",
                len(audio_data),
                source_lang,
                target_lang,
            )

            # This ensures we don't start the next chunk until this one is done.
            # It prevents the server from getting stuck/overloaded and ensures order.
            await process_audio_chunk(
                websocket, audio_data, source_lang, target_lang, user_id, conversation_id
            )

    except WebSocketDisconnect:
        logger.info("WebSocket client %s disconnected.", client_host)
    except Exception as e:
        logger.error("WebSocket error with client %s: %s", client_host, e, exc_info=True)
        await websocket.close()
    finally:
        logger.info("Closing WebSocket connection handler for %s.", client_host)


async def process_audio_chunk(
    websocket: WebSocket,
    audio_data: bytes,
    source_lang: str,
    target_lang: str,
    user_id: str,
    conversation_id: str,
):
    """
    Process audio chunk: transcribe, detect language, translate, and save to database
    """
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            # Step 1: Send to STT service
            files = {"audio_file": ("chunk.wav", audio_data, "audio/wav")}

            stt_response = await client.post(f"{STT_SERVICE_URL}/transcribe", files=files)
            stt_response.raise_for_status()
            stt_data = stt_response.json()
            
            original_text = stt_data.get("transcription", "")
            detected_language = stt_data.get("detected_language", source_lang)
            language_probability = stt_data.get("language_probability", 0.0)

            if not original_text or not original_text.strip():
                logger.info("No transcription detected in chunk.")
                await websocket.send_json({
                    "original_text": "",
                    "translated_text": "",
                    "detected_language": detected_language,
                    "language_probability": language_probability,
                })
                return

            logger.info(
                "STT result: '%s' (detected language: %s, probability: %.2f)",
                original_text,
                detected_language,
                language_probability,
            )

            # Use detected language if confidence is reasonable (>0.3 instead of 0.5)
            effective_source_lang = detected_language if language_probability > 0.3 else source_lang

            logger.info(
                "Language decision: using '%s' (detected: '%s' with %.2f confidence, provided: '%s')",
                effective_source_lang,
                detected_language,
                language_probability,
                source_lang,
            )

            # Step 2: Translate the text
            translation_payload = {
                "text": original_text,
                "source_lang": effective_source_lang,
                "target_lang": target_lang,
            }

            translation_response = await client.post(
                f"{TRANSLATION_SERVICE_URL}/translate", json=translation_payload
            )
            translation_response.raise_for_status()
            translated_text = translation_response.json().get("translated_text", "")
            logger.info("Translation result: '%s'", translated_text)

            # Step 3: Save to database
            try:
                # Ensure db is available
                if hasattr(websocket.app.state, "db"):
                    db = websocket.app.state.db
                    translations_collection = db.get_collection("translations")
                    translation_log = {
                        "original_text": original_text,
                        "translated_text": translated_text,
                        "source_lang": effective_source_lang,
                        "target_lang": target_lang,
                        "detected_language": detected_language,
                        "language_probability": language_probability,
                        "userId": user_id,
                        # Fallback to generating a new ID if one wasn't provided
                        "conversationId": conversation_id or str(uuid4()),
                        "timestamp": datetime.now(UTC),
                    }
                    await translations_collection.insert_one(translation_log)
                    logger.info(
                        f"Saved translation to database (userId: {user_id}, "
                        f"detected_lang: {detected_language}, confidence: {language_probability:.2f})"
                    )
            except Exception as e:
                logger.warning(
                    "Failed to save WebSocket translation to database: %s", e, exc_info=True
                )

            # Step 4: Send result back
            response = {
                "original_text": original_text,
                "translated_text": translated_text,
                "detected_language": detected_language,
                "language_probability": language_probability,
            }

            await websocket.send_json(response)

    except httpx.HTTPError as e:
        logger.error("HTTP error during audio chunk processing: %s", e, exc_info=True)
        error_response = {"original_text": "", "translated_text": f"Error: {str(e)}"}
        await websocket.send_json(error_response)

    except Exception as e:
        logger.error("Error processing audio chunk: %s", e, exc_info=True)
        try:
            error_response = {"original_text": "", "translated_text": f"Processing error: {str(e)}"}
            await websocket.send_json(error_response)
        except WebSocketDisconnect:
            logger.warning("Could not send error to client as they disconnected.")
