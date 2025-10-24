from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()


class Req(BaseModel):
    text: str
    source_lang: str
    target_lang: str


@app.post("/translate")
def translate(req: Req):
    return {"translated_text": f"[{req.target_lang}] {req.text}"}


@app.get("/health")
def health():
    return {"status": "ok"}


