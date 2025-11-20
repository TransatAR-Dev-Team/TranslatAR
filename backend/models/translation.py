from pydantic import BaseModel


class TranslationResponse(BaseModel):
    original_text: str
    translated_text: str
    summary_text: str | None = None
