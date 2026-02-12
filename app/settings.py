import os
from pathlib import Path

from dotenv import load_dotenv
from pydantic_settings import BaseSettings

_PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(_PROJECT_ROOT / ".env")


class Settings(BaseSettings):
    LLM_API_KEY: str = os.getenv("LLM_API_KEY")
    LLM_BASE_URL: str = os.getenv("LLM_BASE_URL")
    LLM_MODEL: str = os.getenv("LLM_MODEL")
    LLM_REQUEST_TIMEOUT: int = 30
    LLM_MAX_RETRIES: int = 3
    KROKI_BASE_URL: str = os.getenv("KROKI_BASE_URL")
    KROKI_MERMAID_PNG_ENDPOINT: str = os.getenv("KROKI_MERMAID_PNG_ENDPOINT")


settings = Settings()
