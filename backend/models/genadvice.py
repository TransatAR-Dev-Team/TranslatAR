from pydantic import BaseModel


class adviceRequest(BaseModel):
    text: str


class adviceResponse(BaseModel):
    advice: str
