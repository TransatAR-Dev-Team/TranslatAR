import httpx
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://ollama:11434")
MODEL_NAME = os.getenv("OLLAMA_MODEL", "phi3:mini")

app = FastAPI()

PROMPT_TEMPLATE = """
You are a helpful assistant that provides advice like a language coach.

Given the following conversation transcript, give clear and constructive advice on how the
speaker can improve their communication. Focus on tone, clarity, grammer, and pacing. Use bullet
points where appropriate and keep it supportive.

Transcript:
{{TRANSCRIPT}}
"""


class adviceRequest(BaseModel):
    text: str

class adviceResponse(BaseModel):
    advice: str


@app.post("/advice", response_model=adviceResponse)
async def advise(request: adviceRequest):
    prompt = (PROMPT_TEMPLATE.replace("{{TRANSCRIPT}}", request.text))
    payload = {"model": MODEL_NAME, "prompt": prompt, "stream": False}


    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(f"{OLLAMA_URL}/v1/generate", json=payload)
            response.raise_for_status()
            data = response.json()

            if "response" not in data:
                raise HTTPException(status_code=500, detail=f"Invalid response from Ollama: {data}")

            return adviceResponse(advice=data["response"].strip())

    except httpx.RequestError as e:
        raise HTTPException(status_code=503, detail=f"Error connecting to Ollama: {e}") from e
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=500, detail=f"Ollama failed: {e}") from e
