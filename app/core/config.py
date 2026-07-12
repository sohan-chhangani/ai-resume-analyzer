from typing import Set

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DATABASE_URL: str

    UPLOAD_DIR: str = "uploads"

    ALLOWED_EXTENSIONS: Set[str] = {
        ".pdf",
        ".docx",
    }

    MAX_UPLOAD_SIZE_BYTES: int = 5 * 1024 * 1024

    ALLOWED_MIME_TYPES: Set[str] = {
        "application/pdf",
        (
            "application/vnd.openxmlformats-officedocument."
            "wordprocessingml.document"
        ),
    }

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )


settings = Settings()