from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",  # ignore any env vars you aren't using yet
    )

    DATABASE_URL: str = "sqlite:///./app.db"
    JWT_SECRET: str = "dev-secret"
    JWT_ALG: str = "HS256"

    JWT_EXPIRE_MINUTES: int = Field(default=60, validation_alias="jwt_expire_minutes")
    REDIS_URL: str = "redis://localhost:6379/0"

settings = Settings()
