import os

import httpx
from fastapi import APIRouter, HTTPException

from models.summarization import SummarizationRequest, SummarizationResponse

# --- Configuration ---
SUMMARIZATION_SERVICE_URL = os.getenv("SUMMARIZATION_URL", "http://summarization:9002")

router = APIRouter()


@router.post("", response_model=SummarizationResponse)
async def get_summary(request: SummarizationRequest):
    """
    Receives text and a desired length, then forwards to the summarization service.
    """
    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            payload = {"text": request.text, "length": request.length}
            response = await client.post(f"{SUMMARIZATION_SERVICE_URL}/summarize", json=payload)
            response.raise_for_status()
            summary_text = response.json().get("summary")
            if summary_text is None:
                raise HTTPException(status_code=500, detail="Summarization failed.")
            return SummarizationResponse(summary=summary_text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error during summarization: {e}") from e
