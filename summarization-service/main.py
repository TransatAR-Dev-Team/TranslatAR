import os
import httpx
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# The URL for the Ollama service, as defined in docker-compose
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://ollama:11434")
MODEL_NAME = os.getenv("OLLAMA_MODEL", "phi3:mini")

app = FastAPI()

class SummarizationRequest(BaseModel):
    text: str

class SummarizationResponse(BaseModel):
    summary: str

@app.post("/summarize", response_model=SummarizationResponse)
async def summarize(request: SummarizationRequest):
    # This prompt can be customized to improve summary quality
    prompt = f"Please provide a concise summary of the following text:\n\n{request.text}"
    
    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": False  # We want the full response at once
    }

    logger.info(f"Forwarding summarization request to Ollama with model '{MODEL_NAME}'...")

    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(f"{OLLAMA_URL}/api/generate", json=payload)
            response.raise_for_status()
            data = response.json()

            if "response" not in data:
                logger.error(f"Invalid response from Ollama: {data}")
                raise HTTPException(status_code=500, detail="Invalid response from Ollama.")
            
            return SummarizationResponse(summary=data["response"])

    except httpx.RequestError as e:
        logger.error(f"Could not connect to Ollama: {e}")
        raise HTTPException(status_code=503, detail=f"Error connecting to Ollama: {e}")
    except httpx.HTTPStatusError as e:
        logger.error(f"Ollama returned an error: {e.response.status_code} - {e.response.text}")
        raise HTTPException(status_code=500, detail=f"Ollama failed: {e.response.text}")

@app.get("/health")
def health_check():
    return {"status": "ok", "model": MODEL_NAME}
