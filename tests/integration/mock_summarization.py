from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()


class SummarizeRequest(BaseModel):
    text: str
    length: str = "medium"


@app.post("/summarize")
def summarize(request: SummarizeRequest):
    # Generate a simple mock summary based on text length
    text = request.text
    length = request.length
    
    if not text:
        return {"summary": "Empty text provided."}
    
    # Create different length summaries
    if length == "short":
        summary = f"This is a short summary of the text. Word count: {len(text.split())}"
    elif length == "medium":
        summary = f"This is a medium-length summary of the provided text. The text contains approximately {len(text.split())} words and discusses various topics."
    else:  # long
        summary = f"This is a comprehensive summary of the provided text. The original text contains approximately {len(text.split())} words. It covers multiple topics and provides detailed information. This longer summary format allows for more nuanced understanding of the source material."
    
    return {"summary": summary}


@app.get("/health")
def health():
    return {"status": "ok"}
