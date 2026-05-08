"""
Session Endpoint
================
GET /session/{session_id} — restored transactions, insights, and dashboard summary.
"""

from fastapi import APIRouter, HTTPException, status

from app.schemas.session import SessionDataResponse
from app.services.analysis_session_service import get_session_payload

router = APIRouter()


@router.get(
    "/{session_id}",
    response_model=SessionDataResponse,
    summary="Load persisted analysis session",
)
async def read_session(session_id: str):
    payload = await get_session_payload(session_id)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found or expired.",
        )
    return SessionDataResponse(
        transactions=payload["transactions"],
        insights=payload["insights"],
        summary=payload["summary"],
    )
