from pathlib import Path

from decouple import config
from pydantic_settings import BaseSettings


BASE_DIR = Path(__file__).resolve().parent



class Settings(BaseSettings):
    """Class to hold application's config values."""

    # App configurations
    API_PREFIX: str = config("API_PREFIX", default="/api/v1")
    JWT_SECRET: str = config("JWT_SECRET", default="jwtsecret")
    ALGORITHM: str = config("ALGORITHM", default="HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = config("ACCESS_TOKEN_EXPIRE_MINUTES", default=30)

    # Database configurations
    DB_HOST: str = config("DB_HOST", default="localhost")
    DB_PORT: int = config("DB_PORT", default=5432)
    DB_USER: str = config("DB_USER", default="postgres")
    DB_PASSWORD: str = config("DB_PASSWORD", default="postgres")
    DB_NAME: str = config("DB_NAME", default="postgres")
    DB_TYPE: str = config("DB_TYPE", default="postgresql")


settings = Settings()