import asyncio
import json
import logging
import os
from datetime import UTC, datetime

import httpx
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from security.auth import verify_jwt_token
from services.conversation_service import ConversationService

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

    # Store userId and conversation_id for this connection
    user_id = None
    conversation_id = None
    conversation_service = None

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

        # Start conversation session (for authenticated users)
        if user_id:
            conversation_service = ConversationService(websocket.app.state.db)
            conversation_id = await conversation_service.start_conversation(
                user_id=user_id,
                source_lang=source_lang,
                target_lang=target_lang,
            )
            logger.info(f"Started conversation: {conversation_id} for user: {user_id}")

        asyncio.create_task(
            process_audio_chunk(
                websocket,
                audio_data,
                source_lang,
                target_lang,
                user_id,
                conversation_id,
            )
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

            logger.info(
                "Received audio chunk from user %s (conv: %s): %d bytes, lang: %s -> %s",
                user_id or "NO USER ID",
                conversation_id or "NO CONV",
                len(audio_data),
                source_lang,
                target_lang,
            )

            asyncio.create_task(
                process_audio_chunk(
                    websocket,
                    audio_data,
                    source_lang,
                    target_lang,
                    user_id,
                    conversation_id,
                )
            )

    except WebSocketDisconnect:
        logger.info("WebSocket client %s disconnected.", client_host)
    except Exception as e:
        logger.error("WebSocket error with client %s: %s", client_host, e, exc_info=True)
        await websocket.close()
    finally:
        # End conversation session
        if conversation_id and conversation_service:
            try:
                await conversation_service.end_conversation(conversation_id)
                logger.info(f"Ended conversation: {conversation_id}")
            except Exception as e:
                logger.warning(f"Failed to end conversation {conversation_id}: {e}")
        logger.info("Closing WebSocket connection handler for %s.", client_host)


async def process_audio_chunk(
    websocket: WebSocket,
    audio_data: bytes,
    source_lang: str,
    target_lang: str,
    user_id: str,
    conversation_id: str = None,
):
    """
    Process audio chunk: transcribe, translate, and save to database with conversation tracking
    """
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            # Step 1: Send to STT service
            files = {"audio_file": ("chunk.wav", audio_data, "audio/wav")}

            stt_response = await client.post(f"{STT_SERVICE_URL}/transcribe", files=files)
            stt_response.raise_for_status()
            original_text = stt_response.json().get("transcription", "")

            if not original_text or not original_text.strip():
                logger.info("No transcription detected in chunk.")
                await websocket.send_json({
                    "original_text": "",
                    "translated_text": "",
                    "conversation_id": conversation_id,
                })
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

            # Step 3: Save to database (with conversation tracking if available)
            try:
                db = websocket.app.state.db

                if conversation_id:
                    # Add translation to conversation session
                    conversation_service = ConversationService(db)
                    await conversation_service.add_translation_to_conversation(
                        conversation_id=conversation_id,
                        original_text=original_text,
                        translated_text=translated_text,
                        source_lang=source_lang,
                        target_lang=target_lang,
                        user_id=user_id,
                    )
                    logger.info(
                        f"Saved translation to conversation {conversation_id} (userId: {user_id})"
                    )
                else:
                    # Save using legacy method (backward compatibility)
                    translations_collection = db.get_collection("translations")
                    translation_log = {
                        "original_text": original_text,
                        "translated_text": translated_text,
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

            # Step 4: Send result back to Unity (with conversation_id)
            response = {
                "original_text": original_text,
                "translated_text": translated_text,
                "conversation_id": conversation_id,
            }

            await websocket.send_json(response)

    except httpx.HTTPError as e:
        logger.error("HTTP error during audio chunk processing: %s", e, exc_info=True)
        error_response = {
            "original_text": "",
            "translated_text": f"Error: {str(e)}",
            "conversation_id": conversation_id,
        }
        await websocket.send_json(error_response)

    except Exception as e:
        logger.error("Error processing audio chunk: %s", e, exc_info=True)
        try:
            error_response = {
                "original_text": "",
                "translated_text": f"Processing error: {str(e)}",
                "conversation_id": conversation_id,
            }
            await websocket.send_json(error_response)
        except WebSocketDisconnect:
            logger.warning("Could not send error to client as they disconnected.")
