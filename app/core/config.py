from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from app.paths import paths


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=paths.BASE_DIR / ".env",
        env_file_encoding="utf-8",
    )

    PROJECT_NAME: str = "FastAPI To-Do"
    DATABASE_URL: str = ""
    DEBUG: bool = True

    @field_validator("DATABASE_URL")
    @classmethod
    def validate_database_url(cls, value: str) -> str:
        if not value or not value.strip():
            raise ValueError("DATABASE_URL must be set in environment or .env")
        return value


settings = Settings()
