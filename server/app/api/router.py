"""
API Router
==========
Central router that aggregates all endpoint modules.
Sub-routers will be registered here as they are implemented.
"""

from fastapi import APIRouter

api_router = APIRouter()


# ---------------------------------------------------------------------------
# Sub-routers
# ---------------------------------------------------------------------------
from app.api.endpoints import (
    upload, parse, categorize, analyze, profile,
    transactions, insights, dashboard, report, session as session_ep,
)

api_router.include_router(upload.router,       prefix="/upload",       tags=["upload"])
api_router.include_router(parse.router,        prefix="/parse",        tags=["parse"])
api_router.include_router(categorize.router,   prefix="/categorize",   tags=["categorize"])
api_router.include_router(analyze.router,      prefix="/analyze",      tags=["analyze"])
api_router.include_router(profile.router,      prefix="/profile",      tags=["profile"])
api_router.include_router(transactions.router, prefix="/transactions", tags=["transactions"])
api_router.include_router(insights.router,     prefix="/insights",     tags=["insights"])
api_router.include_router(dashboard.router,    prefix="/dashboard",    tags=["dashboard"])
api_router.include_router(report.router,       prefix="/report",       tags=["report"])
api_router.include_router(session_ep.router,   prefix="/session",      tags=["session"])
# ---------------------------------------------------------------------------


@api_router.get("/ping", tags=["health"])
async def ping():
    """Quick health-check for the API layer."""
    return {"message": "pong"}
