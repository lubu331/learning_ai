import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:///./school_quiz.db"
    SECRET_KEY: str = "super-secret-local-key-change-this"  # In prod, load from .env
    ALGORITHM: str = "HS256"

    class Config:
        env_file = ".env"


settings = Settings()