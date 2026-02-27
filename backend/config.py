"""Application configuration — loads environment variables."""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env from the project root (one level up from backend/)
_env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(_env_path, override=True)


class Settings:
    LLM_API_KEY: str = os.getenv("LLM_API_KEY", "")
    API_BASE_URL: str = os.getenv("API_BASE_URL", "https://api.fireworks.ai/inference/v1")

    # ── Ordered model list for cascading fallback ───────────────────────────
    MODEL_IDS: list[str] = [
        m
        for m in [
            os.getenv("MODEL_PRIMARY", ""),
            os.getenv("MODEL_SECONDARY", ""),
            os.getenv("MODEL_TERTIARY", ""),
        ]
        if m  # skip any that are empty / unset
    ]

    # How many times to retry each model before moving to the next
    MAX_RETRIES_PER_MODEL: int = int(os.getenv("MAX_RETRIES_PER_MODEL", "1"))

    SYSTEM_PROMPT: str = os.getenv(
        "SYSTEM_PROMPT",
        "You are a helpful financial advisor who explains things clearly to users. "
        "You provide accurate, well-structured financial guidance. "
        "Use examples and simple language when possible.",
    )


settings = Settings()
