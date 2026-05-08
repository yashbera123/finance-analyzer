"""
Report Endpoint
===============
GET /report/{file_id} — generates and returns a PDF financial report.
"""

from fastapi import APIRouter, HTTPException, status
from fastapi.responses import Response

from app.services.store import get_results
from app.services.report import generate_report

router = APIRouter()


@router.get(
    "/{file_id}",
    summary="Download PDF report",
    description="Generates a comprehensive PDF financial analysis report.",
    response_class=Response,
)
async def download_report(file_id: str):
    """
    Generate and return a PDF report for the given file_id.
    """
    results = get_results(file_id)
    if not results:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No results found for file_id: {file_id}. Upload a file first.",
        )

    if not results.analysis_result or not results.profile_result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Incomplete analysis. Re-upload the file.",
        )

    # Build dashboard-style data dict for the report
    analysis = results.analysis_result
    profile_result = results.profile_result
    cat_result = results.categorization_result

    # Summary cards (same logic as dashboard endpoint)
    savings = analysis.savings
    summary_cards = [
        {
            "icon": "💰",
            "label": "Total Income",
            "value": f"₹{savings.total_income:,.2f}",
            "subtitle": f"{savings.savings_ratio}% savings rate",
        },
        {
            "icon": "💳",
            "label": "Total Spending",
            "value": f"₹{savings.total_spending:,.2f}",
            "subtitle": f"{len([t for t in cat_result.transactions if t.transaction_type == 'debit'])} transactions",
        },
        {
            "icon": "🏦",
            "label": "Net Savings",
            "value": f"₹{savings.net_savings:,.2f}",
            "subtitle": f"{savings.savings_ratio}% savings rate",
        },
        {
            "icon": "📊",
            "label": "Health Score",
            "value": f"{profile_result.profile.scores.overall}/100",
            "subtitle": profile_result.profile.personality.value.replace("_", " ").title(),
        },
    ]

    # Top anomalies
    top_anomalies = [
        {
            "description": a.description,
            "amount": a.amount,
            "date": a.transaction_date,
            "reason": a.reason,
        }
        for a in analysis.anomalies.anomalies[:5]
    ]

    dashboard_data = {
        "summary_cards": summary_cards,
        "top_anomalies": top_anomalies,
        # Pass raw analysis objects for chart generation
        "_analysis_trends": analysis.trends,
        "_analysis_categories": analysis.categories,
    }

    insights_data = {
        "profile": profile_result.profile.model_dump(),
        "recommendations": [r.model_dump() for r in profile_result.recommendations],
        "total_potential_savings": profile_result.total_potential_savings,
    }

    # Generate PDF
    pdf_bytes = generate_report(dashboard_data, insights_data)

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="finance_report_{file_id}.pdf"',
        },
    )
