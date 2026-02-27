"""FastAPI application entry-point."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.config import settings
from backend.routers import chat, tools

app = FastAPI(
    title="Finance Chatbot API",
    description="AI-powered financial advisor with calculator tools",
    version="1.0.0",
)

# ── CORS ─────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ──────────────────────────────────────────────────────────────────
app.include_router(chat.router)
app.include_router(tools.router)


@app.get("/")
def root():
    return {"status": "ok", "message": "Finance Chatbot API is running 🚀"}


@app.get("/health")
def health():
    return {
        "status": "healthy",
        "models": settings.MODEL_IDS,
        "fallback_chain": " → ".join(settings.MODEL_IDS) or "⚠️ No models configured",
    }
