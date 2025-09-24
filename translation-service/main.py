import os
import httpx
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

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
    Receives a translation request, forwards it to LibreTranslate,
    and returns a simplified response.
    """
    # Prepare the request for the LibreTranslate API format
    payload = {
        "q": request.text,
        "source": request.source_lang,
        "target": request.target_lang,
        "format": "text"
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(f"{LIBRETRANSLATE_URL}/translate", json=payload)
            response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)
            
            data = response.json()
            
            if "translatedText" not in data:
                raise HTTPException(status_code=500, detail="Invalid response from translation engine.")

            return TranslationResponse(translated_text=data["translatedText"])

    except httpx.RequestError as e:
        raise HTTPException(status_code=503, detail=f"Error connecting to translation engine: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")

@app.get("/health")
def health_check():
    return {"status": "ok", "provider": "libretranslate"}
