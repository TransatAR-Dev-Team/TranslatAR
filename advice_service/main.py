import httpx
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
import traceback

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://ollama:11434")
MODEL_NAME = os.getenv("OLLAMA_MODEL", "phi3:mini")

app = FastAPI()

PROMPT_TEMPLATE = """
You are a helpful language coach.

Given this conversation transcript, give **short, constructive advice** to improve:
- Tone
- Clarity
- Grammar
- Pacing

Use **2-3 bullet points maximum**. Keep it supportive and easy to read.

Transcript:
{{TRANSCRIPT}}
"""


class adviceRequest(BaseModel):
    text: str


class adviceResponse(BaseModel):
    advice: str


@app.post("/advice", response_model=adviceResponse)
async def advise(request: adviceRequest):
    prompt = PROMPT_TEMPLATE.replace("{{TRANSCRIPT}}", request.text)
    payload = {"model": MODEL_NAME, "prompt": prompt, "stream": False}

    try:
        async with httpx.AsyncClient(timeout=300.0) as client:
            response = await client.post(
                f"{OLLAMA_URL}/api/generate",
                json=payload,
            )
            response.raise_for_status()
            data = response.json()

            if "response" not in data:
                raise HTTPException(
                    status_code=500,
                    detail="Invalid response from Ollama"
                )

            return adviceResponse(advice=data["response"].strip())

    except Exception as e:
        print("=== ERROR IN ADVICE SERVICE ===")
        traceback.print_exc()
        # ⬇️ THIS is the fix your tests require
        raise HTTPException(
            status_code=500,
            detail=f"Error: {str(e)}"
        )
