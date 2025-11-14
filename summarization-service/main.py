import logging
import os

import httpx
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

logging.basicConfig(level=logging.INFO, format="%(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://ollama:11434")
MODEL_NAME = os.getenv("OLLAMA_MODEL", "phi3:mini")

app = FastAPI()

LENGTH_PROMPTS = {
    "short": "Summarize the following text in one to two sentences.",
    "medium": "Provide a concise summary of the following text, covering the main points.",
    "long": "Provide a detailed summary of the following text, including key details and nuances.",
}


class SummarizationRequest(BaseModel):
    text: str
    length: str = "medium"


class SummarizationResponse(BaseModel):
    summary: str


@app.post("/summarize", response_model=SummarizationResponse)
async def summarize(request: SummarizationRequest):
    logger.info(f"Received summarization request with length: {request.length}")
    instruction = LENGTH_PROMPTS.get(request.length, LENGTH_PROMPTS["medium"])
    prompt = f"{instruction}\n\n{request.text}"

    payload = {"model": MODEL_NAME, "prompt": prompt, "stream": False}

    logger.info(
        "Forwarding summarization request with length '%s' to model '%s' at URL '%s'...",
        request.length,
        MODEL_NAME,
        OLLAMA_URL,
    )
    logger.debug(f"Ollama payload: {payload}")

    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(f"{OLLAMA_URL}/api/generate", json=payload)
            logger.info(f"Ollama response status code: {response.status_code}")
            logger.debug(f"Ollama raw response: {response.text}")
            response.raise_for_status()
            data = response.json()

            if "response" not in data:
                logger.error(f"Invalid response from Ollama: {data}")
                raise HTTPException(
                    status_code=500, detail="Invalid response from Ollama."
                )

            summary_text = data["response"].strip()
            logger.info(
                f"Successfully generated summary. Length: {len(summary_text)} chars."
            )
            return SummarizationResponse(summary=summary_text)

    except httpx.RequestError as e:
        logger.error(f"Could not connect to Ollama: {e}")
        raise HTTPException(
            status_code=503, detail=f"Error connecting to Ollama: {e}"
        ) from e
    except httpx.HTTPStatusError as e:
        logger.error(
            f"Ollama returned an error: {e.response.status_code} - {e.response.text}"
        )
        raise HTTPException(status_code=500, detail=f"Ollama failed: {e}") from e
    except Exception as e:
        logger.error(
            f"An unexpected error occurred during summarization: {e}", exc_info=True
        )
        raise HTTPException(
            status_code=500, detail="An unexpected error occurred."
        ) from e


@app.get("/health")
def health_check():
    return {"status": "ok", "model": MODEL_NAME}
