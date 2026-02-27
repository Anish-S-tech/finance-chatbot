"""Chat API router — standard and streaming endpoints."""

from __future__ import annotations
import json
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from backend.models.schemas import ChatRequest, ChatResponse
from backend.services.llm_service import generate_response, generate_stream

router = APIRouter(prefix="/api/chat", tags=["Chat"])


@router.post("/", response_model=ChatResponse)
def chat(req: ChatRequest):
    """Non-streaming chat completion with model fallback."""
    try:
        reply, model_used = generate_response(req.message, req.history)
        return ChatResponse(reply=reply, model_used=model_used)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"LLM error: {exc}")


@router.post("/stream")
def chat_stream(req: ChatRequest):
    """Server-Sent Events streaming chat completion with model fallback."""

    def event_generator():
        try:
            model_used = None
            for token, model_id in generate_stream(req.message, req.history):
                if model_used is None:
                    model_used = model_id
                    # Send the model info as the first event
                    yield f"data: {json.dumps({'model_used': model_used})}\n\n"
                if token:  # skip the empty sentinel token
                    yield f"data: {json.dumps({'token': token})}\n\n"
            yield f"data: {json.dumps({'done': True})}\n\n"
        except Exception as exc:
            yield f"data: {json.dumps({'error': str(exc)})}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )
