from fastapi import FastAPI, UploadFile, File

app = FastAPI()


@app.post("/transcribe")
async def transcribe(audio_file: UploadFile = File(...)):
    _ = await audio_file.read()
    return {"transcription": "hello world"}


@app.get("/health")
def health():
    return {"status": "ok"}


