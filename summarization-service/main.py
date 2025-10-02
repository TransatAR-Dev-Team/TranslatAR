import os
import httpx
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://ollama:11434")
MODEL_NAME = os.getenv("OLLAMA_MODEL", "phi3:mini")

app = FastAPI()

LENGTH_PROMPTS = {
    "short": "Summarize the following text in one to two sentences.",
    "medium": "Provide a concise summary of the following text, covering the main points.",
    "long": "Provide a detailed summary of the following text, including key details and nuances."
}

class SummarizationRequest(BaseModel):
    text: str
    length: str = "medium"

class SummarizationResponse(BaseModel):
    summary: str

@app.post("/summarize", response_model=SummarizationResponse)
async def summarize(request: SummarizationRequest):
    instruction = LENGTH_PROMPTS.get(request.length, LENGTH_PROMPTS["medium"])
    prompt = f"{instruction}\n\n{request.text}"
    
    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": False
    }

    logger.info(f"Forwarding summarization request with length '{request.length}' to model '{MODEL_NAME}'...")

    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(f"{OLLAMA_URL}/api/generate", json=payload)
            response.raise_for_status()
            data = response.json()

            if "response" not in data:
                logger.error(f"Invalid response from Ollama: {data}")
                raise HTTPException(status_code=500, detail="Invalid response from Ollama.")
            
            return SummarizationResponse(summary=data["response"].strip())

    except httpx.RequestError as e:
        logger.error(f"Could not connect to Ollama: {e}")
        raise HTTPException(status_code=503, detail=f"Error connecting to Ollama: {e}")
    except httpx.HTTPStatusError as e:
        logger.error(f"Ollama returned an error: {e.response.status_code} - {e.response.text}")
        raise HTTPException(status_code=500, detail=f"Ollama failed: {e.response.text}")

@app.get("/health")
def health_check():
    return {"status": "ok", "model": MODEL_NAME}
