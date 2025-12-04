from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class HistoryItem(BaseModel):
    original_text: str
    translated_text: str
    source_lang: str
    target_lang: str
    timestamp: datetime
    userId: Optional[str] = None
    detected_language: Optional[str] = None
    language_probability: Optional[float] = None


class HistoryResponse(BaseModel):
    history: list[HistoryItem]
