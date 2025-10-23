import logging
import os

import httpx
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

LIBRETRANSLATE_URL = os.getenv("LIBRETRANSLATE_URL", "http://libretranslate:5000")

app = FastAPI()


class TranslationRequest(BaseModel):
    text: str
    source_lang: str
    target_lang: str


class TranslationResponse(BaseModel):
    translated_text: str


@app.post("/translate", response_model=TranslationResponse)
async def translate(request: TranslationRequest):
    payload = {
        "q": request.text,
        "source": request.source_lang,
        "target": request.target_lang,
        "format": "text",
    }

    logger.info(f"Forwarding translation request: {payload}")

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{LIBRETRANSLATE_URL}/translate", json=payload
            )
            response.raise_for_status()
            data = response.json()
            if "translatedText" not in data:
                logger.error(
                    f"Invalid response from translation engine: {data}"
                )  # <-- Add log
                raise HTTPException(
                    status_code=500, detail="Invalid response from translation engine."
                )
            return TranslationResponse(translated_text=data["translatedText"])

    except httpx.RequestError as e:
        logger.error(f"Could not connect to translation engine: {e}")  # <-- Add log
        raise HTTPException(
            status_code=503, detail=f"Error connecting to translation engine: {e}"
        )
    except httpx.HTTPStatusError as e:
        logger.error(
            f"Translation engine returned an error: {e.response.status_code} - {e.response.text}"
        )  # <-- Add log
        raise HTTPException(
            status_code=500, detail=f"Translation engine failed: {e.response.text}"
        )
    except Exception as e:
        logger.error(f"An unexpected error occurred: {str(e)}")  # <-- Add log
        raise HTTPException(
            status_code=500, detail=f"An unexpected error occurred: {str(e)}"
        )


@app.get("/health")
def health_check():
    return {"status": "ok", "provider": "libretranslate"}
