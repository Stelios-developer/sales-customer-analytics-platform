from pathlib import Path
from pydantic_settings import BaseSettings
from pydantic_settings import SettingsConfigDict
from typing import List


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    APP_NAME: str = "Sales Analytics API"
    APP_VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"

    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/sales_db"
    SQLITE_DATABASE_URL: str = "sqlite:///./sales_test.db"

    UPLOAD_DIR: str = "uploads"
    ARTIFACT_DIR: str = "artifacts"
    MAX_UPLOAD_SIZE_MB: int = 20

    BACKEND_CORS_ORIGINS: str = "http://localhost:5173"

    @property
    def cors_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.BACKEND_CORS_ORIGINS.split(",")]


settings = Settings()

# Ensure directories exist
Path(settings.UPLOAD_DIR).mkdir(parents=True, exist_ok=True)
Path(settings.ARTIFACT_DIR).mkdir(parents=True, exist_ok=True)
