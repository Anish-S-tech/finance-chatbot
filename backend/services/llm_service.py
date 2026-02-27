"""LLM service — wraps the OpenAI-compatible Fireworks client with cascading
model fallback.  Tries each model in settings.MODEL_IDS in order; if one
fails, falls back to the next."""

from __future__ import annotations

import logging
from typing import List, Tuple

from openai import OpenAI
from backend.config import settings
from backend.models.schemas import ChatMessage

logger = logging.getLogger(__name__)

_client = OpenAI(
    base_url=settings.API_BASE_URL,
    api_key=settings.LLM_API_KEY,
)


# ── Helpers ──────────────────────────────────────────────────────────────────

def _build_messages(history: List[ChatMessage], user_message: str) -> list[dict]:
    """Build the messages payload for the API call."""
    messages = [{"role": "system", "content": settings.SYSTEM_PROMPT}]
    for msg in history:
        messages.append({"role": msg.role, "content": msg.content})
    messages.append({"role": "user", "content": user_message})
    return messages


# ── Non-streaming with fallback ──────────────────────────────────────────────

def generate_response(
    user_message: str,
    history: List[ChatMessage],
) -> Tuple[str, str]:
    """Non-streaming completion with cascading model fallback.

    Returns
    -------
    (reply_text, model_id)
        The generated text and the ID of the model that produced it.
    """
    messages = _build_messages(history, user_message)
    last_exc: Exception | None = None

    for model_id in settings.MODEL_IDS:
        for attempt in range(1, settings.MAX_RETRIES_PER_MODEL + 1):
            try:
                logger.info(
                    "Trying model %s (attempt %d/%d)",
                    model_id, attempt, settings.MAX_RETRIES_PER_MODEL,
                )
                response = _client.chat.completions.create(
                    model=model_id,
                    messages=messages,
                    max_tokens=1024,
                    temperature=0.7,
                )
                logger.info("✅ Success with model %s", model_id)
                return response.choices[0].message.content, model_id

            except Exception as exc:
                last_exc = exc
                logger.warning(
                    "❌ Model %s attempt %d failed: %s", model_id, attempt, exc,
                )

    # All models exhausted
    raise RuntimeError(
        f"All {len(settings.MODEL_IDS)} models failed. Last error: {last_exc}"
    )


# ── Streaming with fallback ──────────────────────────────────────────────────

def generate_stream(
    user_message: str,
    history: List[ChatMessage],
):
    """Streaming completion with cascading model fallback.

    Yields
    ------
    (token, model_id) tuples.
    The first yielded item is always ("", model_id) so callers can capture the
    model name even before any real tokens arrive.
    """
    messages = _build_messages(history, user_message)
    last_exc: Exception | None = None

    for model_id in settings.MODEL_IDS:
        for attempt in range(1, settings.MAX_RETRIES_PER_MODEL + 1):
            try:
                logger.info(
                    "Streaming: trying model %s (attempt %d/%d)",
                    model_id, attempt, settings.MAX_RETRIES_PER_MODEL,
                )
                stream = _client.chat.completions.create(
                    model=model_id,
                    messages=messages,
                    max_tokens=1024,
                    temperature=0.7,
                    stream=True,
                )

                logger.info("✅ Stream opened with model %s", model_id)
                # Sentinel so callers know which model was used
                yield "", model_id

                for chunk in stream:
                    delta = chunk.choices[0].delta
                    if delta and delta.content:
                        yield delta.content, model_id

                return  # success — stop trying other models

            except Exception as exc:
                last_exc = exc
                logger.warning(
                    "❌ Stream model %s attempt %d failed: %s",
                    model_id, attempt, exc,
                )

    # All models exhausted
    raise RuntimeError(
        f"All {len(settings.MODEL_IDS)} models failed. Last error: {last_exc}"
    )
