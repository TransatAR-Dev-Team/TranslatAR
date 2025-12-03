import logging
import os

import httpx
from fastapi import APIRouter, HTTPException

from models.genadvice import adviceRequest, adviceResponse

# --- Configuration ---
ADVICE_SERVICE_URL = os.getenv("ADVICE_URL", "http://advice:9003")
logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("", response_model=adviceResponse)
async def get_advice(request: adviceRequest):
    """
    Receives text, then forwards to the advice generation service.
    """
    try:
        async with httpx.AsyncClient(timeout=600.0) as client:
            payload = {"text": request.text}
            logger.info(f"Forwarding advice request to {ADVICE_SERVICE_URL}/advice")
            response = await client.post(f"{ADVICE_SERVICE_URL}/advice", json=payload)
            response.raise_for_status()
            advice_text = response.json().get("advice")
            if advice_text is None:
                logger.error("Advice service returned response without 'advice' field")
                raise HTTPException(status_code=500, detail="Advice generation failed.")
            return adviceResponse(advice=advice_text)
    except httpx.RequestError as e:
        logger.error(f"Could not connect to advice service at {ADVICE_SERVICE_URL}: {e}")
        raise HTTPException(
            status_code=503,
            detail=f"Advice service is unavailable. Please check if the service is running."
        ) from e
    except httpx.HTTPStatusError as e:
        logger.error(f"Advice service returned error: {e.response.status_code} - {e.response.text}")
        error_detail = f"Advice service error: {e.response.status_code}"
        try:
            error_body = e.response.json()
            if "detail" in error_body:
                error_detail = error_body["detail"]
        except Exception:
            error_detail = e.response.text or error_detail
        raise HTTPException(status_code=500, detail=error_detail) from e
    except Exception as e:
        logger.error(f"Unexpected error during advice generation: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error during advice generation: {str(e)}") from e
