"""
Finance Analyzer — Backend Entry Point
=======================================
FastAPI application with CORS middleware and modular router setup.
"""

import os
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_router
from app.services.analysis_session_service import initialize_session_store

# ---------------------------------------------------------------------------
# Environment
# ---------------------------------------------------------------------------
load_dotenv()

CORS_ORIGINS = [
    origin.strip()
    for origin in os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")
    if origin.strip()
]
APP_ENV = os.getenv("APP_ENV", "development")


# ---------------------------------------------------------------------------
# Lifespan (startup / shutdown hooks)
# ---------------------------------------------------------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan — runs on startup and shutdown."""
    print(f"🚀 Finance Analyzer API starting in [{APP_ENV}] mode")

    # Attempt database table creation
    try:
        # Import models so Base.metadata registers all tables
        import app.models  # noqa: F401
        from app.core.database import create_tables

        await create_tables()
        print("✅ Database tables ready")
    except Exception as e:
        print(f"⚠️  Database not available — running without persistence: {e}")

    try:
        await initialize_session_store()
        print("✅ Session store ready")
    except Exception as e:
        print(f"⚠️  Session store not available — using in-memory fallback: {e}")

    yield

    # Shutdown: cleanup
    try:
        from app.core.database import engine
        await engine.dispose()
    except Exception:
        pass
    print("🛑 Finance Analyzer API shutting down")


# ---------------------------------------------------------------------------
# Application
# ---------------------------------------------------------------------------
app = FastAPI(
    title="AI Personal Finance Behavior Analyzer",
    description="Analyzes financial behavior using AI-driven categorization, anomaly detection, and profiling.",
    version="0.1.0",
    lifespan=lifespan,
    docs_url="/docs" if APP_ENV == "development" else None,
    redoc_url="/redoc" if APP_ENV == "development" else None,
)


# ---------------------------------------------------------------------------
# Middleware
# ---------------------------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Routers
# ---------------------------------------------------------------------------
app.include_router(api_router, prefix="/api/v1")


# ---------------------------------------------------------------------------
# Health check (root)
# ---------------------------------------------------------------------------
@app.get("/", tags=["health"])
async def root():
    return {
        "status": "healthy",
        "service": "finance-analyzer-api",
        "version": "0.1.0",
        "environment": APP_ENV,
    }


@app.get("/health", tags=["health"])
async def health_check():
    return {"status": "ok"}


# ---------------------------------------------------------------------------
# Production entrypoint (for local `python main.py`)
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", "8000"))
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=APP_ENV == "development",
    )
