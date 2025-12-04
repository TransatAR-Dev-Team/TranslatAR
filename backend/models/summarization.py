from pydantic import BaseModel


class SummarizationRequest(BaseModel):
    text: str
    length: str = "medium"


class SummarizationResponse(BaseModel):
    summary: str


class SummarySaveRequest(BaseModel):
    summary: str
    original_text: str
    conversationId: str | None = None
