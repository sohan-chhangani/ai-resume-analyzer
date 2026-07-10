from typing import Set

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DATABASE_URL: str

    UPLOAD_DIR: str = "uploads"

    ALLOWED_EXTENSIONS: Set[str] = {
        ".pdf",
        ".docx",
    }

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )


settings = Settings()
