# config.py
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    JWT_SECRET: str = "dev-secret-123"
    OPENAI_API_KEY: str | None = None
    DATABASE_URL: str = "sqlite:///./mood.db"

settings = Settings()


