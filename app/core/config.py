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
    JWT_SECRET: str = ""
    DEBUG: bool = True

    # JWT settings
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    JWT_ISSUER: str = "todo-app"
    JWT_AUDIENCE: str = "todo-app-clients"

    @field_validator("DATABASE_URL")
    @classmethod
    def validate_database_url(cls, value: str) -> str:
        if not value or not value.strip():
            raise ValueError("DATABASE_URL must be set in environment or .env")
        return value

    @field_validator("JWT_SECRET")
    @classmethod
    def validate_jwt_secret(cls, value: str) -> str:
        if not value or not value.strip():
            raise ValueError("JWT_SECRET must be set in environment or .env")
        return value

    @field_validator("JWT_ACCESS_TOKEN_EXPIRE_MINUTES")
    @classmethod
    def validate_jwt_access_token_expire_minutes(cls, value: int) -> int:
        if value <= 0:
            raise ValueError(
                "JWT_ACCESS_TOKEN_EXPIRE_MINUTES must be a positive integer"
            )
        return value

    @field_validator("REFRESH_TOKEN_EXPIRE_DAYS")
    @classmethod
    def validate_refresh_token_expire_days(cls, value: int) -> int:
        if value <= 0:
            raise ValueError("REFRESH_TOKEN_EXPIRE_DAYS must be a positive integer")
        return value


settings = Settings()
