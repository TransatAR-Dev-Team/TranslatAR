from pydantic import BaseModel


class SettingsModel(BaseModel):
    source_language: str = "en"
    target_language: str = "es"
    chunk_duration_seconds: float = 8.0
    target_sample_rate: int = 48000
    silence_threshold: float = 0.01
    chunk_overlap_seconds: float = 0.5
    websocket_url: str = "ws://localhost:8000/ws"


class SettingsResponse(BaseModel):
    settings: SettingsModel
