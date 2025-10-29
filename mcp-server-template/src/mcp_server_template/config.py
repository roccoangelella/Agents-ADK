# src/mcp_server_template/config.py
from pathlib import Path
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict

LOG_LEVEL_TYPE = Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]

class Settings(BaseSettings):
    """
    Defines and validates server settings, loaded from a .env file.
    The server will fail to start if required settings are missing or invalid.
    """
    SERVER_NAME: str = "MCP-Server-Template"
    LOG_LEVEL: LOG_LEVEL_TYPE = "INFO"
    LOG_FILE: Path = Path("logs/server.log")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )

# Create a single, validated settings instance to be used across the application.
settings = Settings()
