"""
Dashboard Endpoint
==================
GET /dashboard/{file_id} — returns pre-aggregated data for the frontend
dashboard: summary cards, chart data, recent transactions, and profile summary.
"""

import logging
from fastapi import APIRouter, HTTPException, status

from app.schemas.dashboard import DashboardResponse
from app.services.dashboard_builder import build_dashboard_data
from app.services.store import get_results

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get(
    "/{file_id}",
    response_model=DashboardResponse,
    summary="Get dashboard data",
    description="Returns pre-aggregated data ready for frontend rendering: "
                "summary cards, chart data, recent transactions, and profile.",
)
async def get_dashboard(file_id: str):
    """
    Build dashboard-ready data from cached analysis results.
    """
    results = get_results(file_id)
    if not results:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No data found for file_id: {file_id}. Upload a file first.",
        )

    analysis = results.analysis_result
    profile = results.profile_result
    cat_result = results.categorization_result

    if not analysis or not profile or not cat_result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Incomplete analysis. Re-upload the file.",
        )

    dashboard_data = build_dashboard_data(file_id, results)

    response = DashboardResponse(
        data=dashboard_data,
    )
    logger.info("Dashboard response file_id=%s payload=%s", file_id, response.model_dump(mode="json"))
    return response
