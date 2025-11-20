from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class AdviceRequest(BaseModel):
    text: str

@app.post("/advice")
def generate_advice(request: AdviceRequest):
    # Return a static response immediately
    return {"advice": "This is a mock advice for integration testing."}
