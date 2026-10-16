import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]

class Settings:
    APP_NAME = os.getenv("APP_NAME", "AI Hub")
    APP_VERSION = os.getenv("APP_VERSION", "1.0.0")
    API_V1_PREFIX = os.getenv("API_V1_PREFIX", "/api/v1")
    DEBUG = os.getenv("DEBUG", "false").lower() == "true"
    HOST = os.getenv("HOST", "127.0.0.1")
    PORT = int(os.getenv("PORT", "8000"))
    UPLOAD_DIR = Path(os.getenv("UPLOAD_DIR", str(PROJECT_ROOT / "uploads")))
    DATA_DIR = Path(os.getenv("DATA_DIR", str(PROJECT_ROOT / "data")))
    LOG_DIR = Path(os.getenv("LOG_DIR", str(PROJECT_ROOT / "logs")))
    MAX_UPLOAD_MB = int(os.getenv("MAX_UPLOAD_MB", "10"))

settings = Settings()
