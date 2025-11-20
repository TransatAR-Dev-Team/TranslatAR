<<<<<<< Updated upstream
import logging
=======

>>>>>>> Stashed changes
import os

import httpx
from fastapi import APIRouter, HTTPException

from models.summarization import SummarizationRequest, SummarizationResponse

# --- Configuration ---
SUMMARIZATION_SERVICE_URL = os.getenv("SUMMARIZATION_URL", "http://summarization:9002")

# --- Logger Setup ---
logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("", response_model=SummarizationResponse)
async def get_summary(request: SummarizationRequest):
    """
    Receives text and a desired length, then forwards to the summarization service.
    """
    logger.info(
        "Received request: summarize text of length %d with length '%s'.",
        len(request.text),
        request.length,
    )
    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            payload = {"text": request.text, "length": request.length}
            logger.info(
                "Forwarding request to summarization service at %s/summarize",
                SUMMARIZATION_SERVICE_URL,
            )
            response = await client.post(
                f"{SUMMARIZATION_SERVICE_URL}/summarize", json=payload
            )

            logger.info(
                "Received response with status code %d from summarization service.",
                response.status_code,
            )

            response.raise_for_status()
            summary_text = response.json().get("summary")
            if summary_text is None:
                logger.error(
                    "Summarization service returned a successful status code "
                    "but the response did not contain a 'summary' key."
                )
                raise HTTPException(status_code=500, detail="Summarization failed.")

            logger.info("Successfully received summary from summarization service.")
            return SummarizationResponse(summary=summary_text)
    except httpx.RequestError as e:
        logger.error(
            f"Could not connect to the summarization service at {SUMMARIZATION_SERVICE_URL}: {e}",
            exc_info=True,
        )
        raise HTTPException(
            status_code=503,
            detail="The summarization service is currently unavailable.",
        ) from e
    except httpx.HTTPStatusError as e:
        logger.error(
            "The summarization service returned an error: %d - %s",
            e.response.status_code,
            e.response.text,
            exc_info=True,
        )
        raise HTTPException(
            status_code=e.response.status_code,
            detail=f"Summarization service failed: {e.response.text}",
        ) from e
    except Exception as e:
        logger.error(
            f"An unexpected error occurred while processing the summarization request: {e}",
            exc_info=True,
        )
        raise HTTPException(
            status_code=500, detail=f"Error during summarization: {e}"
        ) from e
