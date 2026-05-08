"""
Insights Endpoint
=================
GET /insights/{file_id} — returns the financial profile, scores,
and actionable recommendations.
"""

from fastapi import APIRouter, HTTPException, status

from app.schemas.profile import ProfileResponse
from app.services.store import get_results

router = APIRouter()


@router.get(
    "/{file_id}",
    response_model=ProfileResponse,
    summary="Get financial insights and recommendations",
    description="Returns spending personality, risk level, financial scores, "
                "strengths, weaknesses, and actionable recommendations.",
)
async def get_insights(file_id: str):
    """
    Retrieve the full financial profile and recommendations.
    """
    results = get_results(file_id)
    if not results or not results.profile_result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No insights found for file_id: {file_id}. Upload a file first.",
        )

    return ProfileResponse(
        status="success",
        message="Financial insights ready",
        data=results.profile_result,
    )
