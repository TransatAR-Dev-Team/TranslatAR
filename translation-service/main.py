import logging
import os

import httpx
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

logging.basicConfig(level=logging.INFO, format="%(name)s - %(levelname)s - %(message)s")
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
    """
    Translate text from one language to another using LibreTranslate service.
    This async function forwards a translation request to an external LibreTranslate API
    and returns the translated text.
    Args:
        request (TranslationRequest): A translation request object containing:
            - text (str): The text to be translated
            - source_lang (str): The source language code
            - target_lang (str): The target language code
    Returns:
        TranslationResponse: A response object containing:
            - translated_text (str): The translated text from the LibreTranslate service
    Raises:
        HTTPException:
            - 503 status: When unable to connect to the LibreTranslate service
            - 500 status: When the translation engine returns an error or invalid response
            - 500 status: When an unexpected error occurs during translation
    Logs:
        - info: When forwarding the translation request and upon successful translation
        - error: When connection fails, invalid responses occur, or unexpected errors happen
    """

    payload = {
        "q": request.text,
        "source": request.source_lang,
        "target": request.target_lang,
        "format": "text",
    }

    logger.info(
        "Forwarding translation request for lang '%s'->'%s' to %s",
        request.source_lang,
        request.target_lang,
        LIBRETRANSLATE_URL,
    )

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(f"{LIBRETRANSLATE_URL}/translate", json=payload)
            response.raise_for_status()
            data = response.json()
            if "translatedText" not in data:
                logger.error("Invalid response from translation engine: %s", data)
                raise HTTPException(
                    status_code=500, detail="Invalid response from translation engine."
                )

            translated_text = data["translatedText"]
            logger.info(
                "Successfully received translation. Result length: %d chars.",
                len(translated_text),
            )
            return TranslationResponse(translated_text=translated_text)

    except httpx.RequestError as e:
        logger.error("Could not connect to translation engine: %s", e, exc_info=True)
        raise HTTPException(
            status_code=503, detail=f"Error connecting to translation engine: {e}"
        ) from e
    except httpx.HTTPStatusError as e:
        logger.error(
            "Translation engine returned an error: %s - %s",
            e.response.status_code,
            e.response.text,
        )
        raise HTTPException(status_code=500, detail=f"Translation engine failed: {e}") from e
    except Exception as e:
        logger.error("An unexpected error occurred: %s", str(e), exc_info=True)
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {e}") from e


@app.get("/health")
def health_check():
    return {"status": "ok", "provider": "libretranslate"}
