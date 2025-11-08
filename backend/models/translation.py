from pydantic import BaseModel


class TranslationResponse(BaseModel):
    original_text: str
    translated_text: str
