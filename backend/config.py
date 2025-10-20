import os
from dotenv import load_dotenv

# --- Service URLs ---
STT_SERVICE_URL = os.getenv("STT_SERVICE_URL", "http://stt:9000")
TRANSLATION_SERVICE_URL = os.getenv("TRANSLATION_SERVICE_URL", "http://translation:9001")
SUMMARIZATION_SERVICE_URL = os.getenv("SUMMARIZATION_SERVICE_URL", "http://summarization:9002")

# --- Database ---
DATABASE_URL = os.getenv("DATABASE_URL", "mongodb://mongodb:27017")
