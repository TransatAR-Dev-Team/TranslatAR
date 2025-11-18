from datetime import datetime

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, validator

from services.transcript_service import fetch_transcripts

router = APIRouter()

class TranscriptQuery(BaseModel):
    limit: int = 50
    since: datetime | None = None
    user_id: str | None = None

    @validator("limit")
    def validate_limit(cls, value: int) -> int:
        if value <= 0 or value > 500:
            raise ValueError("limit must be between 1 and 500.")
        return value


@router.post("", response_model=list[dict])
async def get_transcripts(request: Request, query: TranscriptQuery):
    try:
        transcripts = await fetch_transcripts(
            request.app.state.db,
            limit=query.limit,
            since=query.since,
            user_id=query.user_id,
        )
        return transcripts
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to load transcripts: {exc}") from exc