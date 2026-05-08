"""
Analysis Schemas
================
Models for behavioral analysis results: trends, recurring patterns,
anomalies, savings ratio, and the full analysis report.
"""

import datetime
from typing import Dict, List, Optional

from pydantic import BaseModel, Field

from app.schemas.category import Category


# ═══════════════════════════════════════════════════════════════════════════
# Monthly Trends
# ═══════════════════════════════════════════════════════════════════════════

class MonthlyTrend(BaseModel):
    """Spending/income data for a single month."""

    month: str = Field(..., description="YYYY-MM format")
    total_spending: float = 0.0
    total_income: float = 0.0
    net: float = 0.0
    transaction_count: int = 0
    avg_transaction: float = 0.0


class TrendAnalysis(BaseModel):
    """Monthly trend analysis across the date range."""

    months: List[MonthlyTrend] = Field(default_factory=list)
    avg_monthly_spending: float = 0.0
    avg_monthly_income: float = 0.0
    spending_trend: str = Field(
        "stable", description="increasing | decreasing | stable"
    )
    highest_spend_month: Optional[str] = None
    lowest_spend_month: Optional[str] = None


# ═══════════════════════════════════════════════════════════════════════════
# Category Breakdown
# ═══════════════════════════════════════════════════════════════════════════

class CategorySpend(BaseModel):
    """Spending data for a single category."""

    category: str
    label: str
    total: float = 0.0
    percentage: float = 0.0
    count: int = 0
    avg_per_transaction: float = 0.0


class CategoryAnalysis(BaseModel):
    """Full category breakdown analysis."""

    breakdown: List[CategorySpend] = Field(default_factory=list)
    top_3_categories: List[str] = Field(default_factory=list)
    most_frequent_category: Optional[str] = None
    total_categories_used: int = 0


# ═══════════════════════════════════════════════════════════════════════════
# Recurring Transactions
# ═══════════════════════════════════════════════════════════════════════════

class RecurringTransaction(BaseModel):
    """A detected recurring spending pattern."""

    description: str
    category: str
    amount: float
    frequency: str = Field(
        ..., description="weekly | biweekly | monthly | irregular"
    )
    occurrences: int
    total_spent: float
    dates: List[str] = Field(default_factory=list)
    is_subscription: bool = False


class RecurringAnalysis(BaseModel):
    """Summary of recurring transaction patterns."""

    recurring_transactions: List[RecurringTransaction] = Field(default_factory=list)
    total_recurring_count: int = 0
    total_recurring_amount: float = 0.0
    estimated_monthly_recurring: float = 0.0


# ═══════════════════════════════════════════════════════════════════════════
# Savings Ratio
# ═══════════════════════════════════════════════════════════════════════════

class SavingsAnalysis(BaseModel):
    """Savings ratio and related metrics."""

    total_income: float = 0.0
    total_spending: float = 0.0
    net_savings: float = 0.0
    savings_ratio: float = Field(0.0, description="Savings as % of income")
    rating: str = Field(
        "unknown",
        description="excellent | good | fair | poor | critical | unknown",
    )
    recommendation: str = ""


# ═══════════════════════════════════════════════════════════════════════════
# Anomaly Detection
# ═══════════════════════════════════════════════════════════════════════════

class Anomaly(BaseModel):
    """A single anomalous transaction."""

    row_index: int
    transaction_date: Optional[str] = Field(None, alias="date")
    description: str
    amount: float
    category: str
    anomaly_score: float = Field(
        ..., description="Isolation Forest score (lower = more anomalous)"
    )
    reason: str = ""

    model_config = {"populate_by_name": True, "serialize_by_alias": True}


class AnomalyAnalysis(BaseModel):
    """Anomaly detection results."""

    anomalies: List[Anomaly] = Field(default_factory=list)
    total_anomalies: int = 0
    anomaly_rate: float = Field(0.0, description="% of transactions flagged")
    method: str = "isolation_forest"


# ═══════════════════════════════════════════════════════════════════════════
# Full Analysis Report
# ═══════════════════════════════════════════════════════════════════════════

class AnalysisResult(BaseModel):
    """Complete behavioral analysis report."""

    file_id: str
    trends: TrendAnalysis
    categories: CategoryAnalysis
    recurring: RecurringAnalysis
    savings: SavingsAnalysis
    anomalies: AnomalyAnalysis
    analyzed_at: datetime.datetime


class AnalysisResponse(BaseModel):
    """API response wrapper."""

    status: str = "success"
    message: str = "Behavioral analysis complete"
    data: AnalysisResult
