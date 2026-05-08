"""
Dashboard Schemas
=================
Pre-aggregated data structures for frontend dashboard rendering.
"""

from typing import List, Optional

from pydantic import BaseModel, Field


class SummaryCard(BaseModel):
    """Single metric card for dashboard header."""

    label: str
    value: str
    subtitle: str = ""
    icon: str = ""
    trend: Optional[str] = None  # "up" | "down" | "stable"


class ChartPoint(BaseModel):
    """Generic data point for charts."""

    label: str
    value: float
    color: Optional[str] = None


class RecentTransaction(BaseModel):
    """Slim transaction for the dashboard list."""

    date: Optional[str]
    description: str
    amount: float
    type: str
    category: str
    icon: str = ""


class DashboardData(BaseModel):
    """All data needed to render the frontend dashboard."""

    file_id: str
    summary_cards: List[SummaryCard] = Field(default_factory=list)
    monthly_trends: List[dict] = Field(
        default_factory=list,
        description="Array of {month, spending, income, net} for line/bar chart",
    )
    category_breakdown: List[ChartPoint] = Field(
        default_factory=list, description="For pie/donut chart"
    )
    recent_transactions: List[RecentTransaction] = Field(default_factory=list)
    top_anomalies: List[dict] = Field(default_factory=list)
    recurring_items: List[dict] = Field(default_factory=list)
    profile_summary: dict = Field(default_factory=dict)
    recommendations: List[dict] = Field(default_factory=list)


class DashboardResponse(BaseModel):
    """API response wrapper."""

    status: str = "success"
    message: str = "Dashboard data ready"
    data: DashboardData
