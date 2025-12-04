import logging
import os
from datetime import UTC, datetime

import httpx
from fastapi import APIRouter, Depends, HTTPException, Request

from models.summarization import SummarizationRequest, SummarizationResponse, SummarySaveRequest
from security.auth import get_current_user

SUMMARIZATION_SERVICE_URL = os.getenv("SUMMARIZATION_URL", "http://summarization:9002")

logger = logging.getLogger(__name__)

MIN_WORDS_MEDIUM = 100
MIN_WORDS_LONG = 300

router = APIRouter()


def determine_appropriate_length(text: str, requested_length: str) -> tuple[str, str | None]:
    word_count = len(text.split())

    if word_count < MIN_WORDS_MEDIUM:
        max_appropriate = "short"
    elif word_count < MIN_WORDS_LONG:
        max_appropriate = "medium"
    else:
        max_appropriate = "long"

    length_order = {"short": 1, "medium": 2, "long": 3}
    requested_level = length_order.get(requested_length, 2)
    max_level = length_order.get(max_appropriate, 2)

    if requested_level > max_level:
        actual_length = max_appropriate
        message = (
            f"Your text was too short for a {requested_length} summary, "
            f"so a {actual_length} summary was generated instead."
        )
        return actual_length, message

    return requested_length, None


@router.post("", response_model=SummarizationResponse)
async def get_summary(request: SummarizationRequest):
    logger.info(
        "Received request: summarize text of length %d with length '%s'.",
        len(request.text),
        request.length,
    )
    try:
        actual_length, notification_message = determine_appropriate_length(
            request.text, request.length
        )

        async with httpx.AsyncClient(timeout=120.0) as client:
            payload = {"text": request.text, "length": actual_length}
            logger.info(
                "Forwarding request to summarization service at %s/summarize",
                SUMMARIZATION_SERVICE_URL,
            )
            response = await client.post(f"{SUMMARIZATION_SERVICE_URL}/summarize", json=payload)

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
            return SummarizationResponse(summary=summary_text, message=notification_message)
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
        raise HTTPException(status_code=500, detail=f"Error during summarization: {e}") from e


@router.post("/save")
async def save_summary(
    payload: SummarySaveRequest,
    request: Request,
    current_user: dict = Depends(get_current_user),  # noqa: B008
):
    if not current_user:
        raise HTTPException(status_code=401, detail="Unauthorized")

    summary = payload.summary
    original_text = payload.original_text

    if not summary or not original_text:
        raise HTTPException(status_code=400, detail="Missing summary or original_text")

    summaries = request.app.state.summaries

    doc = {
        "userId": str(current_user["_id"]),
        "original_text": original_text,
        "summary": summary,
        "created_at": datetime.now(UTC),
    }

    result = await summaries.insert_one(doc)

    return {"status": "saved", "summary_id": str(result.inserted_id)}


@router.get("/history")
async def get_summary_history(
    request: Request,
    current_user: dict = Depends(get_current_user),  # noqa: B008
):
    if not current_user:
        raise HTTPException(status_code=401, detail="Unauthorized")

    summaries = request.app.state.summaries
    cursor = summaries.find({"userId": str(current_user["_id"])}).sort("created_at", -1)

    history = []
    async for doc in cursor:
        doc["_id"] = str(doc["_id"])
        history.append(doc)

    return {"history": history}
