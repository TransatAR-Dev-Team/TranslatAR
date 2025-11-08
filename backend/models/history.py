from datetime import datetime

from pydantic import BaseModel


class HistoryItem(BaseModel):
    original_text: str
    translated_text: str
    source_lang: str
    target_lang: str
    timestamp: datetime


class HistoryResponse(BaseModel):
    history: list[HistoryItem]
