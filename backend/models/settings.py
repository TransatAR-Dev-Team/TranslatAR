from pydantic import BaseModel


class SettingsModel(BaseModel):
    # Technical fields
    source_language: str = "en"
    target_language: str = "es"
    chunk_duration_seconds: float = 8.0
    target_sample_rate: int = 48000
    silence_threshold: float = 0.01
    chunk_overlap_seconds: float = 0.5
    websocket_url: str = "ws://localhost:8000/ws"

    # UX Fields
    subtitles_enabled: bool = True
    translation_enabled: bool = True
    subtitle_font_size: int = 18
    subtitle_style: str = "normal"


class SettingsResponse(BaseModel):
    settings: SettingsModel
