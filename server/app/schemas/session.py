"""
Session persistence API schemas.
"""

from typing import Any, Dict, List

from pydantic import BaseModel, Field


class AnalyzeSessionResponse(BaseModel):
    """POST /analyze/{file_id} returns only the persisted session id."""

    session_id: str = Field(..., description="UUID for GET /session/{session_id}")


class SessionDataResponse(BaseModel):
    """GET /session/{session_id} — restored pipeline payloads."""

    transactions: List[Any] = Field(default_factory=list)
    insights: Dict[str, Any] = Field(default_factory=dict)
    summary: Dict[str, Any] = Field(default_factory=dict)
