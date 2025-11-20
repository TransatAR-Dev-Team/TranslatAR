from pydantic import BaseModel


class SummarizationRequest(BaseModel):
    text: str
    length: str = "medium"


class SummarizationResponse(BaseModel):
    summary: str
    message: str | None = None
