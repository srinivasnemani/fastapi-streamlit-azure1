from typing import List

from pydantic import ConfigDict
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Application settings
    """

    model_config = ConfigDict(env_file=".env")

    # API Settings
    api_title: str = "Portfolio Analytics API"
    api_version: str = "1.0.0"
    api_description: str = "API for portfolio analytics and trading data"

    # Database Settings
    # Default to SQLite, can be overridden by .env for other DBs
    database_url: str = "sqlite:///./backend/database/portfolio_data.sqlite"

    # Security Settings
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    # CORS Settings
    allow_origins: List[str] = ["*"]
    allow_credentials: bool = True
    allow_methods: List[str] = ["*"]
    allow_headers: List[str] = ["*"]


settings = Settings()
