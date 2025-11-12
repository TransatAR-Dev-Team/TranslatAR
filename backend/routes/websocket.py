import asyncio
import json
import os
from datetime import UTC, datetime

import httpx
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from security.auth import verify_jwt_token

router = APIRouter()

# Service URLs from environment
STT_SERVICE_URL = os.getenv("STT_URL", "http://stt:9000")
TRANSLATION_SERVICE_URL = os.getenv("TRANSLATION_URL", "http://translation:9001")


@router.websocket("")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    print("Unity client connected!")

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

            print(f"Received audio chunk: {len(audio_data)} bytes")
            print(f"Languages: {source_lang} -> {target_lang}")

            # Process audio in background with userId
            asyncio.create_task(
                process_audio_chunk(websocket, audio_data, source_lang, target_lang, user_id)
            )

    except WebSocketDisconnect:
        print("Unity client disconnected")
    except Exception as e:
        print(f"WebSocket error: {e}")
        await websocket.close()


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
        async with httpx.AsyncClient(timeout=30.0) as client:
            # Step 1: Send to STT service
            files = {"audio_file": ("chunk.wav", audio_data, "audio/wav")}

            stt_response = await client.post(f"{STT_SERVICE_URL}/transcribe", files=files)
            stt_response.raise_for_status()
            original_text = stt_response.json().get("transcription", "")

            if not original_text or original_text.strip() == "":
                print("No transcription detected in chunk")
                await websocket.send_json({"original_text": "", "translated_text": ""})
                return

            print(f"Transcribed: {original_text}")

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

            print(f"Translated: {translated_text}")

            # Step 3: Save to database
            try:
                db = websocket.app.state.db
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
                print(f"Saved translation to database (userId: {user_id})")
            except Exception as e:
                print(f"WARNING: Failed to save translation to database: {e}")

            # Step 4: Send result back to Unity
            response = {
                "original_text": original_text,
                "translated_text": translated_text,
            }

            await websocket.send_json(response)

    except httpx.HTTPError as e:
        print(f"HTTP error during processing: {e}")
        error_response = {"original_text": "", "translated_text": f"Error: {str(e)}"}
        await websocket.send_json(error_response)

    except Exception as e:
        print(f"Error processing audio chunk: {e}")
        error_response = {
            "original_text": "",
            "translated_text": f"Processing error: {str(e)}",
        }
        await websocket.send_json(error_response)
