import asyncio
import json
import logging
import os
from datetime import UTC, datetime

import httpx
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from security.auth import verify_jwt_token

logger = logging.getLogger(__name__)

router = APIRouter()

# Service URLs from environment
STT_SERVICE_URL = os.getenv("STT_URL", "http://stt:9000")
TRANSLATION_SERVICE_URL = os.getenv("TRANSLATION_URL", "http://translation:9001")
SUMMARIZATION_SERVICE_URL = os.getenv("SUMMARIZATION_URL", "http://summarization:9002")


@router.websocket("")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    client_host = websocket.client.host if websocket.client else "unknown"
    logger.info("WebSocket client connected from: %s", client_host)

    # Store userId for this connection
    user_id = None

    try:
        while True:
            # Receive binary message from Unity
            data = await websocket.receive_bytes()

            # Parse the message format: [4 bytes length][metadata JSON][audio WAV]
            metadata_length = int.from_bytes(data[:4], byteorder="little")
            metadata_json = data[4 : 4 + metadata_length].decode("utf-8")
            audio_data = data[4 + metadata_length :]

            # Parse metadata
            metadata = json.loads(metadata_json)
            source_lang = metadata.get("source_lang", "en")
            target_lang = metadata.get("target_lang", "es")

            # Check for JWT token in metadata
            jwt_token = metadata.get("jwt_token")
            if jwt_token:
                verified_user_id = await verify_jwt_token(jwt_token)
                if verified_user_id:
                    user_id = verified_user_id
                    print(f"Authenticated user: {user_id}")

            # Process audio in background with userId
            logger.info(
                "Received audio chunk from user %s: %d bytes, lang: %s -> %s",
                user_id or "NO USER ID",
                len(audio_data),
                source_lang,
                target_lang,
            )

            asyncio.create_task(
                process_audio_chunk(websocket, audio_data, source_lang, target_lang, user_id)
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
):
    """
    Process audio chunk: transcribe, translate, and save to database
    """
    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            # Step 1: Send to STT service
            files = {"audio_file": ("chunk.wav", audio_data, "audio/wav")}

            stt_response = await client.post(f"{STT_SERVICE_URL}/transcribe", files=files)
            stt_response.raise_for_status()
            original_text = stt_response.json().get("transcription", "")

            if not original_text or not original_text.strip():
                logger.info("No transcription detected in chunk.")
                await websocket.send_json({"original_text": "", "translated_text": ""})
                return

            logger.info("STT result: '%s'", original_text)

            # Step 2: Translate the text
            translation_payload = {
                "text": original_text,
                "source_lang": source_lang,
                "target_lang": target_lang,
            }

            translation_response = await client.post(
                f"{TRANSLATION_SERVICE_URL}/translate", json=translation_payload
            )
            translation_response.raise_for_status()
            translated_text = translation_response.json().get("translated_text", "")
            logger.info("Translation result: '%s'", translated_text)

            # Step 3: Ensure we have English text for summarization
            english_text = original_text if source_lang.lower() == "en" else None
            if target_lang.lower() == "en":
                english_text = translated_text

            if english_text is None:
                english_payload = {
                    "text": original_text,
                    "source_lang": source_lang,
                    "target_lang": "en",
                }
                english_response = await client.post(
                    f"{TRANSLATION_SERVICE_URL}/translate", json=english_payload
                )
                english_response.raise_for_status()
                english_text = english_response.json().get("translated_text", "")

            if not english_text:
                raise ValueError("Failed to obtain English text for summarization.")

            # Step 4: Summarize using Ollama
            summary_payload = {"text": english_text, "length": "medium"}
            summary_response = await client.post(
                f"{SUMMARIZATION_SERVICE_URL}/summarize", json=summary_payload
            )
            summary_response.raise_for_status()
            summary_text = summary_response.json().get("summary", "")

            if not summary_text:
                raise ValueError("Summarization service returned empty summary.")

            # Step 5: Save to database
            try:
                db = websocket.app.state.db
                translations_collection = db.get_collection("translations")
                translation_log = {
                    "original_text": original_text,
                    "translated_text": translated_text,
                    "summary_text": summary_text,
                    "source_lang": source_lang,
                    "target_lang": target_lang,
                    "userId": user_id,
                    "timestamp": datetime.now(UTC),
                }
                await translations_collection.insert_one(translation_log)
                logger.info(f"Saved translation to database (userId: {user_id})")
            except Exception as e:
                logger.warning(
                    "Failed to save WebSocket translation to database: %s", e, exc_info=True
                )

            # Step 6: Send result back to Unity
            response = {
                "original_text": original_text,
                "translated_text": translated_text,
                "summary_text": summary_text,
            }

            await websocket.send_json(response)

    except httpx.HTTPError as e:
<<<<<<< Updated upstream
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
=======
        print(f"HTTP error during processing: {e}")
        error_response = {
            "original_text": "",
            "translated_text": f"Error: {str(e)}",
            "summary_text": "",
        }
        await websocket.send_json(error_response)

    except Exception as e:
        print(f"Error processing audio chunk: {e}")
        error_response = {
            "original_text": "",
            "translated_text": f"Processing error: {str(e)}",
            "summary_text": "",
        }
        await websocket.send_json(error_response)
>>>>>>> Stashed changes
