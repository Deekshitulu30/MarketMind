import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List

# Base directory for the backend
BASE_DIR = Path(__file__).resolve().parent.parent.parent

class Settings(BaseSettings):
    APP_NAME: str = "MarketMind"
    ENVIRONMENT: str = "development"
    LOG_LEVEL: str = "INFO"
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = "supersecretmarketmindkey_dev_only"

    # Server settings
    BACKEND_HOST: str = "0.0.0.0"
    BACKEND_PORT: int = 8000
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
        "http://localhost:80",
        "http://localhost"
    ]

    # Database
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        f"sqlite:///{BASE_DIR.parent / 'data' / 'marketmind.db'}"
    )

    # Storage Paths
    BASE_DIR: Path = BASE_DIR
    DATA_DIR: Path = BASE_DIR.parent / "data"
    RAW_DATA_DIR: Path = BASE_DIR.parent / "data" / "raw"
    VALIDATED_DATA_DIR: Path = BASE_DIR.parent / "data" / "validated"
    PROCESSED_DATA_DIR: Path = BASE_DIR.parent / "data" / "processed"
    FEATURES_DATA_DIR: Path = BASE_DIR.parent / "data" / "features"
    MODEL_ARTIFACTS_DIR: Path = BASE_DIR.parent / "models" / "artifacts"
    STOCKS_DIR: Path = BASE_DIR.parent / "stocks"
    ETFS_DIR: Path = BASE_DIR.parent / "etfs"

    # ML Defaults
    RANDOM_SEED: int = 42
    DEFAULT_PREDICTION_HORIZON: int = 1
    DEFAULT_FEATURE_VERSION: str = "v1.0"
    DEFAULT_DATASET_VERSION: str = "market-data-v1.0"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )

settings = Settings()

# Ensure directories exist
for path in [
    settings.DATA_DIR,
    settings.RAW_DATA_DIR,
    settings.VALIDATED_DATA_DIR,
    settings.PROCESSED_DATA_DIR,
    settings.FEATURES_DATA_DIR,
    settings.MODEL_ARTIFACTS_DIR
]:
    path.mkdir(parents=True, exist_ok=True)
