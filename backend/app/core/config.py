from __future__ import annotations

import os
from pathlib import Path
from pydantic_settings import BaseSettings

BASE_DIR = Path(__file__).resolve().parent.parent.parent


class Settings(BaseSettings):
    APP_NAME: str = "Fraud Detection API"
    ENVIRONMENT: str = "development"
    SECRET_KEY: str = "dev-secret-key-change-me"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7

    DATABASE_URL: str = f"sqlite:///{BASE_DIR / 'app.db'}"
    UPLOAD_DIR: str = str(BASE_DIR / "uploads")
    MODELS_DIR: str = str(BASE_DIR / "models")
    DATA_DIR: str = str(BASE_DIR / "data")

    CORS_ORIGINS: str = "http://localhost:5173,http://localhost:3000"

    class Config:
        env_file = BASE_DIR / ".env"
        case_sensitive = True


settings = Settings()
