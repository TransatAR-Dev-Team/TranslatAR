import os

import httpx
from fastapi import APIRouter, HTTPException

from models.genadvice import adviceRequest, adviceResponse

# --- Configuration ---
ADVICE_SERVICE_URL = os.getenv("ADVICE_URL", "http://advice:9003")
router = APIRouter()


@router.post("", response_model=adviceResponse)
async def get_advice(request: adviceRequest):
    """
    Receives text, then forwards to the advice generation service.
    """
    try:
        async with httpx.AsyncClient(timeout=300.0) as client:
            payload = {"text": request.text}
            response = await client.post(f"{ADVICE_SERVICE_URL}/advice", json=payload)
            response.raise_for_status()
            advice_text = response.json().get("advice")
            if advice_text is None:
                raise HTTPException(status_code=500, detail="Advice generation failed.")
            return adviceResponse(advice=advice_text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error during advice generation: {e}") from e
