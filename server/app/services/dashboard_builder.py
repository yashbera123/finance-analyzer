"""
Build dashboard-ready payload from in-memory pipeline results.
"""

import logging
from typing import TYPE_CHECKING

from app.schemas.dashboard import (
    ChartPoint,
    DashboardData,
    RecentTransaction,
    SummaryCard,
)

if TYPE_CHECKING:
    from app.services.store import FileResults

logger = logging.getLogger(__name__)

_CATEGORY_ICONS = {
    "food_dining": "🍕",
    "groceries": "🛒",
    "transport": "🚗",
    "shopping": "🛍️",
    "subscriptions": "📱",
    "bills_utilities": "💡",
    "rent_housing": "🏠",
    "health_fitness": "💪",
    "entertainment": "🎬",
    "travel": "✈️",
    "education": "📚",
    "income": "💰",
    "transfer": "🔄",
    "atm_cash": "🏧",
    "insurance": "🛡️",
    "investments": "📈",
    "personal_care": "💇",
    "gifts_donations": "🎁",
    "fees_charges": "🏦",
    "other": "📋",
}

_CATEGORY_COLORS = {
    "food_dining": "#FF6384",
    "groceries": "#36A2EB",
    "transport": "#FFCE56",
    "shopping": "#9966FF",
    "subscriptions": "#FF9F40",
    "bills_utilities": "#4BC0C0",
    "rent_housing": "#C9CBCF",
    "health_fitness": "#7BC043",
    "entertainment": "#F44336",
    "travel": "#2196F3",
    "education": "#9C27B0",
    "income": "#4CAF50",
    "transfer": "#607D8B",
    "atm_cash": "#795548",
    "insurance": "#00BCD4",
    "investments": "#8BC34A",
    "personal_care": "#E91E63",
    "gifts_donations": "#FF5722",
    "fees_charges": "#9E9E9E",
    "other": "#BDBDBD",
}


def build_dashboard_data(file_id: str, results: "FileResults") -> DashboardData:
    """Aggregate dashboard view models from cached pipeline results."""
    analysis = results.analysis_result
    profile = results.profile_result
    cat_result = results.categorization_result

    if not analysis or not profile or not cat_result:
        raise ValueError("Incomplete results for dashboard build")

    savings = analysis.savings
    summary_cards = [
        SummaryCard(
            label="Total Income",
            value=f"₹{savings.total_income:,.2f}",
            icon="💰",
            subtitle=f"{len([t for t in cat_result.transactions if t.transaction_type == 'credit'])} deposits",
        ),
        SummaryCard(
            label="Total Spending",
            value=f"₹{savings.total_spending:,.2f}",
            icon="💳",
            subtitle=f"{len([t for t in cat_result.transactions if t.transaction_type == 'debit'])} transactions",
        ),
        SummaryCard(
            label="Net Savings",
            value=f"₹{savings.net_savings:,.2f}",
            icon="🏦",
            subtitle=f"{savings.savings_ratio}% savings rate",
            trend="up" if savings.net_savings > 0 else "down",
        ),
        SummaryCard(
            label="Health Score",
            value=f"{profile.profile.scores.overall}/100",
            icon="📊",
            subtitle=profile.profile.personality.value.replace("_", " ").title(),
        ),
    ]

    monthly_trends = [
        {
            "month": m.month,
            "spending": m.total_spending,
            "income": m.total_income,
            "net": m.net,
            "transactions": m.transaction_count,
        }
        for m in analysis.trends.months
    ]

    category_breakdown = [
        ChartPoint(
            label=cat.label,
            value=cat.total,
            color=_CATEGORY_COLORS.get(cat.category, "#BDBDBD"),
        )
        for cat in analysis.categories.breakdown
        if cat.total > 0
    ]

    sorted_txns = sorted(
        cat_result.transactions,
        key=lambda t: str(t.transaction_date or "0000-00-00"),
        reverse=True,
    )
    recent_transactions = [
        RecentTransaction(
            date=str(t.transaction_date) if t.transaction_date else None,
            description=t.description or "(no description)",
            amount=t.amount,
            type=t.transaction_type,
            category=t.category_label,
            icon=_CATEGORY_ICONS.get(t.category.value, "📋"),
        )
        for t in sorted_txns[:10]
    ]

    top_anomalies = [
        {
            "description": a.description,
            "amount": a.amount,
            "date": a.transaction_date,
            "reason": a.reason,
            "category": a.category,
            "score": a.anomaly_score,
        }
        for a in analysis.anomalies.anomalies[:5]
    ]

    recurring_items = [
        {
            "description": r.description,
            "amount": r.amount,
            "frequency": r.frequency,
            "is_subscription": r.is_subscription,
            "category": r.category,
            "occurrences": r.occurrences,
        }
        for r in analysis.recurring.recurring_transactions[:8]
    ]

    profile_summary = {
        "personality": profile.profile.personality.value,
        "personality_description": profile.profile.personality_description,
        "risk_level": profile.profile.risk_level.value,
        "scores": profile.profile.scores.model_dump(),
        "strengths": profile.profile.strengths,
        "weaknesses": profile.profile.weaknesses,
    }

    recommendations = [
        {
            "type": r.type.value,
            "priority": r.priority,
            "title": r.title,
            "description": r.description,
            "potential_savings": r.potential_savings,
            "icon": r.icon,
        }
        for r in profile.recommendations
    ]

    data = DashboardData(
        file_id=file_id,
        summary_cards=summary_cards,
        monthly_trends=monthly_trends,
        category_breakdown=category_breakdown,
        recent_transactions=recent_transactions,
        top_anomalies=top_anomalies,
        recurring_items=recurring_items,
        profile_summary=profile_summary,
        recommendations=recommendations,
    )
    logger.info("Dashboard build file_id=%s", file_id)
    return data
