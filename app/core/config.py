from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
import os

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",  # ignore any env vars you aren't using yet
    )

    DATABASE_URL: str = "sqlite:///./app.db"
    JWT_SECRET: str = os.getenv("JWT_SECRET", "local-dev-only-change-me")
    JWT_ALG: str = "HS256"

    JWT_EXPIRE_MINUTES: int = Field(default=60, validation_alias="jwt_expire_minutes")


settings = Settings()
