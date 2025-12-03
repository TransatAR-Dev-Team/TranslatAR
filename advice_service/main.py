import logging
import os
import traceback

import httpx
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://ollama:11434")
MODEL_NAME = os.getenv("OLLAMA_MODEL", "phi3:mini")

logging.basicConfig(level=logging.INFO, format="%(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

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

    logger.info(f"Generating advice using model {MODEL_NAME} at {OLLAMA_URL}")

    try:
        async with httpx.AsyncClient(timeout=600.0) as client:
            response = await client.post(
                f"{OLLAMA_URL}/api/generate",
                json=payload,
            )
            response.raise_for_status()
            data = response.json()

            if "response" not in data:
                logger.error(f"Invalid response from Ollama: {data}")
                raise HTTPException(
                    status_code=500,
                    detail="Invalid response from Ollama"
                )

            advice_text = data["response"].strip()
            logger.info(f"Successfully generated advice. Length: {len(advice_text)} chars.")
            return adviceResponse(advice=advice_text)

    except httpx.RequestError as e:
        logger.error(f"Could not connect to Ollama at {OLLAMA_URL}: {e}", exc_info=True)
        raise HTTPException(
            status_code=503,
            detail=f"Ollama service is unavailable. Please check if Ollama is running."
        ) from e
    except httpx.HTTPStatusError as e:
        logger.error(f"Ollama returned an error: {e.response.status_code} - {e.response.text}")
        raise HTTPException(
            status_code=500,
            detail=f"Ollama failed: {e.response.status_code} - {e.response.text}"
        ) from e
    except Exception as e:
        logger.error("=== ERROR IN ADVICE SERVICE ===", exc_info=True)
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"Error: {str(e)}"
        ) from e
