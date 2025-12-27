from pydantic import BaseModel
from dotenv import load_dotenv
import os

load_dotenv()


class Settings(BaseModel):
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./app.db")
    JWT_SECRET: str = os.getenv("JWT_SECRET", "dev-secret")  # whatever you already use
    JWT_ALG: str = os.getenv("JWT_ALG", "HS256")


settings = Settings()