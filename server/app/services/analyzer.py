"""
Behavioral Analysis Engine
===========================
Five analysis modules:
  1. Monthly spending trends
  2. Category breakdown
  3. Recurring transaction detection
  4. Savings ratio
  5. Anomaly detection (Isolation Forest)

Each module is independent — the top-level `run_analysis()` orchestrates them.
"""

from __future__ import annotations

import datetime
import logging
import re
from collections import defaultdict
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest

from app.schemas.analysis import (
    AnalysisResult,
    Anomaly,
    AnomalyAnalysis,
    CategoryAnalysis,
    CategorySpend,
    MonthlyTrend,
    RecurringAnalysis,
    RecurringTransaction,
    SavingsAnalysis,
    TrendAnalysis,
)
from app.schemas.category import CATEGORY_LABELS, CategorizedTransaction, Category

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════════════════
# 1. Monthly Spending Trends
# ═══════════════════════════════════════════════════════════════════════════

def analyze_trends(transactions: List[CategorizedTransaction]) -> TrendAnalysis:
    """
    Aggregate spending and income by month.
    Detect whether spending is trending up, down, or stable.
    """
    monthly: Dict[str, MonthlyTrend] = {}

    for txn in transactions:
        dt = txn.transaction_date
        if dt is None:
            continue

        month_key = f"{dt.year}-{dt.month:02d}"

        if month_key not in monthly:
            monthly[month_key] = MonthlyTrend(month=month_key)

        mt = monthly[month_key]
        mt.transaction_count += 1

        if txn.transaction_type == "debit":
            mt.total_spending = round(mt.total_spending + txn.amount, 2)
        elif txn.transaction_type == "credit":
            mt.total_income = round(mt.total_income + txn.amount, 2)

    # Finalize each month
    for mt in monthly.values():
        mt.net = round(mt.total_income - mt.total_spending, 2)
        if mt.transaction_count > 0:
            mt.avg_transaction = round(mt.total_spending / max(mt.transaction_count, 1), 2)

    # Sort chronologically
    months_sorted = sorted(monthly.values(), key=lambda m: m.month)

    if not months_sorted:
        return TrendAnalysis()

    # Averages
    avg_spending = round(
        sum(m.total_spending for m in months_sorted) / len(months_sorted), 2
    )
    avg_income = round(
        sum(m.total_income for m in months_sorted) / len(months_sorted), 2
    )

    # Trend detection (simple linear: compare first half avg vs second half avg)
    spending_trend = "stable"
    if len(months_sorted) >= 2:
        mid = len(months_sorted) // 2
        first_half_avg = sum(m.total_spending for m in months_sorted[:mid]) / max(mid, 1)
        second_half_avg = sum(m.total_spending for m in months_sorted[mid:]) / max(len(months_sorted) - mid, 1)

        diff_pct = ((second_half_avg - first_half_avg) / max(first_half_avg, 1)) * 100
        if diff_pct > 10:
            spending_trend = "increasing"
        elif diff_pct < -10:
            spending_trend = "decreasing"

    # Highest / lowest spend months
    spending_months = [m for m in months_sorted if m.total_spending > 0]
    highest = max(spending_months, key=lambda m: m.total_spending).month if spending_months else None
    lowest = min(spending_months, key=lambda m: m.total_spending).month if spending_months else None

    return TrendAnalysis(
        months=months_sorted,
        avg_monthly_spending=avg_spending,
        avg_monthly_income=avg_income,
        spending_trend=spending_trend,
        highest_spend_month=highest,
        lowest_spend_month=lowest,
    )


# ═══════════════════════════════════════════════════════════════════════════
# 2. Category Breakdown
# ═══════════════════════════════════════════════════════════════════════════

def analyze_categories(transactions: List[CategorizedTransaction]) -> CategoryAnalysis:
    """
    Break down spending by category with percentages and averages.
    """
    cat_data: Dict[str, dict] = {}

    total_spending = 0.0

    for txn in transactions:
        if txn.transaction_type != "debit":
            continue

        cat_key = txn.category.value
        if cat_key not in cat_data:
            cat_data[cat_key] = {
                "category": cat_key,
                "label": txn.category_label,
                "total": 0.0,
                "count": 0,
            }

        cat_data[cat_key]["total"] = round(cat_data[cat_key]["total"] + txn.amount, 2)
        cat_data[cat_key]["count"] += 1
        total_spending += txn.amount

    # Build CategorySpend list
    breakdown: List[CategorySpend] = []
    for cd in cat_data.values():
        pct = round((cd["total"] / total_spending) * 100, 1) if total_spending > 0 else 0.0
        avg = round(cd["total"] / cd["count"], 2) if cd["count"] > 0 else 0.0
        breakdown.append(
            CategorySpend(
                category=cd["category"],
                label=cd["label"],
                total=cd["total"],
                percentage=pct,
                count=cd["count"],
                avg_per_transaction=avg,
            )
        )

    # Sort by total descending
    breakdown.sort(key=lambda c: c.total, reverse=True)

    # Top 3 and most frequent
    top_3 = [c.label for c in breakdown[:3]]
    most_frequent = max(breakdown, key=lambda c: c.count).label if breakdown else None

    return CategoryAnalysis(
        breakdown=breakdown,
        top_3_categories=top_3,
        most_frequent_category=most_frequent,
        total_categories_used=len(breakdown),
    )


# ═══════════════════════════════════════════════════════════════════════════
# 3. Recurring Transaction Detection
# ═══════════════════════════════════════════════════════════════════════════

def _normalize_description(desc: str) -> str:
    """Normalize description for grouping similar transactions."""
    d = desc.lower().strip()
    # Remove trailing numbers/codes (common in bank statements)
    d = re.sub(r"\s*#?\d+$", "", d)
    # Remove extra whitespace
    d = re.sub(r"\s+", " ", d)
    return d


def _detect_frequency(dates: List[datetime.date]) -> str:
    """Detect the frequency pattern from a list of dates."""
    if len(dates) < 2:
        return "irregular"

    sorted_dates = sorted(dates)
    gaps = [
        (sorted_dates[i + 1] - sorted_dates[i]).days
        for i in range(len(sorted_dates) - 1)
    ]

    avg_gap = sum(gaps) / len(gaps)

    if 5 <= avg_gap <= 9:
        return "weekly"
    elif 12 <= avg_gap <= 17:
        return "biweekly"
    elif 25 <= avg_gap <= 35:
        return "monthly"
    else:
        return "irregular"


def analyze_recurring(transactions: List[CategorizedTransaction]) -> RecurringAnalysis:
    """
    Detect recurring transactions by grouping similar descriptions
    and analyzing date patterns.
    """
    # Group by normalized description
    groups: Dict[str, List[CategorizedTransaction]] = defaultdict(list)

    for txn in transactions:
        if txn.transaction_type != "debit" or not txn.description:
            continue
        key = _normalize_description(txn.description)
        groups[key].append(txn)

    recurring: List[RecurringTransaction] = []

    for desc_key, txns in groups.items():
        if len(txns) < 2:
            continue

        # Check if amounts are similar (within 20% of each other)
        amounts = [t.amount for t in txns]
        avg_amount = sum(amounts) / len(amounts)
        amount_variance = max(amounts) - min(amounts)
        is_similar_amount = amount_variance <= avg_amount * 0.2

        if not is_similar_amount and len(txns) < 3:
            continue  # Need at least 3 occurrences if amounts vary

        dates = [t.transaction_date for t in txns if t.transaction_date is not None]
        frequency = _detect_frequency(dates)

        # Determine if it's a subscription
        is_subscription = (
            is_similar_amount
            and frequency in ("monthly", "biweekly", "weekly")
        )

        recurring.append(
            RecurringTransaction(
                description=txns[0].description,
                category=txns[0].category_label,
                amount=round(avg_amount, 2),
                frequency=frequency,
                occurrences=len(txns),
                total_spent=round(sum(amounts), 2),
                dates=[str(d) for d in sorted(dates)],
                is_subscription=is_subscription,
            )
        )

    # Sort by total spent
    recurring.sort(key=lambda r: r.total_spent, reverse=True)

    total_recurring_amount = round(sum(r.total_spent for r in recurring), 2)

    # Estimate monthly recurring cost
    monthly_estimate = 0.0
    for r in recurring:
        if r.frequency == "weekly":
            monthly_estimate += r.amount * 4.33
        elif r.frequency == "biweekly":
            monthly_estimate += r.amount * 2.17
        elif r.frequency == "monthly":
            monthly_estimate += r.amount
        else:
            # Irregular: average per month based on date span
            if len(r.dates) >= 2:
                first = datetime.date.fromisoformat(r.dates[0])
                last = datetime.date.fromisoformat(r.dates[-1])
                months_span = max((last - first).days / 30.0, 1.0)
                monthly_estimate += r.total_spent / months_span

    return RecurringAnalysis(
        recurring_transactions=recurring,
        total_recurring_count=len(recurring),
        total_recurring_amount=total_recurring_amount,
        estimated_monthly_recurring=round(monthly_estimate, 2),
    )


# ═══════════════════════════════════════════════════════════════════════════
# 4. Savings Ratio
# ═══════════════════════════════════════════════════════════════════════════

def analyze_savings(transactions: List[CategorizedTransaction]) -> SavingsAnalysis:
    """
    Calculate savings ratio and rate the financial health.
    """
    total_income = round(
        sum(t.amount for t in transactions if t.transaction_type == "credit"), 2
    )
    total_spending = round(
        sum(t.amount for t in transactions if t.transaction_type == "debit"), 2
    )
    net_savings = round(total_income - total_spending, 2)

    # Savings ratio (as % of income)
    if total_income > 0:
        savings_ratio = round((net_savings / total_income) * 100, 1)
    else:
        savings_ratio = 0.0

    # Rating
    if total_income == 0:
        rating = "unknown"
        recommendation = "No income detected — ensure income transactions are included."
    elif savings_ratio >= 30:
        rating = "excellent"
        recommendation = (
            "Outstanding savings discipline! Consider investing surplus funds "
            "for long-term growth."
        )
    elif savings_ratio >= 20:
        rating = "good"
        recommendation = (
            "Healthy savings rate. You're on track — look for opportunities "
            "to optimize recurring expenses."
        )
    elif savings_ratio >= 10:
        rating = "fair"
        recommendation = (
            "Moderate savings rate. Review discretionary spending categories "
            "and consider setting up auto-savings."
        )
    elif savings_ratio >= 0:
        rating = "poor"
        recommendation = (
            "Low savings rate. Prioritize cutting non-essential expenses "
            "and build an emergency fund."
        )
    else:
        rating = "critical"
        recommendation = (
            "Spending exceeds income. Immediately review all expenses, "
            "cut subscriptions, and create a strict budget."
        )

    return SavingsAnalysis(
        total_income=total_income,
        total_spending=total_spending,
        net_savings=net_savings,
        savings_ratio=savings_ratio,
        rating=rating,
        recommendation=recommendation,
    )


# ═══════════════════════════════════════════════════════════════════════════
# 5. Anomaly Detection (Isolation Forest)
# ═══════════════════════════════════════════════════════════════════════════

def analyze_anomalies(
    transactions: List[CategorizedTransaction],
    contamination: float = 0.1,
) -> AnomalyAnalysis:
    """
    Detect anomalous transactions using Isolation Forest.

    Features used:
    - amount (primary signal)
    - day of week
    - day of month

    Contamination controls the expected anomaly rate (default 10%).
    """
    # Filter to debits with valid dates
    debit_txns = [
        t for t in transactions
        if t.transaction_type == "debit" and t.transaction_date is not None
    ]

    if len(debit_txns) < 5:
        # Not enough data for meaningful anomaly detection
        return AnomalyAnalysis(method="isolation_forest")

    # Build feature matrix
    features = []
    for t in debit_txns:
        dt = t.transaction_date
        features.append([
            t.amount,
            dt.weekday(),       # 0=Mon, 6=Sun
            dt.day,             # 1-31
        ])

    X = np.array(features)

    # Fit Isolation Forest
    # Adjust contamination based on dataset size
    effective_contamination = min(contamination, 0.5)
    if len(debit_txns) < 10:
        effective_contamination = min(contamination, 1.0 / len(debit_txns))

    model = IsolationForest(
        n_estimators=100,
        contamination=effective_contamination,
        random_state=42,
    )
    model.fit(X)

    # Score all transactions
    scores = model.decision_function(X)
    predictions = model.predict(X)  # 1 = normal, -1 = anomaly

    anomalies: List[Anomaly] = []

    for i, (txn, score, pred) in enumerate(zip(debit_txns, scores, predictions)):
        if pred == -1:  # Anomaly
            # Generate human-readable reason
            reason = _explain_anomaly(txn, debit_txns)

            anomalies.append(
                Anomaly(
                    row_index=txn.row_index,
                    transaction_date=str(txn.transaction_date) if txn.transaction_date else None,
                    description=txn.description,
                    amount=txn.amount,
                    category=txn.category_label,
                    anomaly_score=round(float(score), 4),
                    reason=reason,
                )
            )

    # Sort by score (most anomalous first)
    anomalies.sort(key=lambda a: a.anomaly_score)

    anomaly_rate = round(
        (len(anomalies) / len(debit_txns)) * 100, 1
    ) if debit_txns else 0.0

    return AnomalyAnalysis(
        anomalies=anomalies,
        total_anomalies=len(anomalies),
        anomaly_rate=anomaly_rate,
        method="isolation_forest",
    )


def _explain_anomaly(
    txn: CategorizedTransaction,
    all_debits: List[CategorizedTransaction],
) -> str:
    """Generate a human-readable explanation for why a transaction is anomalous."""
    amounts = [t.amount for t in all_debits]
    avg = sum(amounts) / len(amounts)
    std = (sum((a - avg) ** 2 for a in amounts) / len(amounts)) ** 0.5

    reasons = []

    # Unusually high amount
    if txn.amount > avg + 2 * std:
        ratio = round(txn.amount / avg, 1)
        reasons.append(f"Amount is {ratio}x the average spending")
    elif txn.amount > avg + std:
        reasons.append("Amount is significantly above average")

    # Unusually low amount (micro-transactions)
    if txn.amount < avg * 0.1 and avg > 10:
        reasons.append("Unusually small transaction")

    # Weekend spending
    if txn.transaction_date and txn.transaction_date.weekday() >= 5:
        reasons.append("Weekend transaction")

    if not reasons:
        reasons.append("Unusual spending pattern detected")

    return "; ".join(reasons)


# ═══════════════════════════════════════════════════════════════════════════
# Orchestrator
# ═══════════════════════════════════════════════════════════════════════════

def run_analysis(
    file_id: str,
    transactions: List[CategorizedTransaction],
) -> AnalysisResult:
    """
    Run all five analysis modules and return the complete report.
    """
    logger.info("Transactions passed to analysis file_id=%s count=%d", file_id, len(transactions))
    result = AnalysisResult(
        file_id=file_id,
        trends=analyze_trends(transactions),
        categories=analyze_categories(transactions),
        recurring=analyze_recurring(transactions),
        savings=analyze_savings(transactions),
        anomalies=analyze_anomalies(transactions),
        analyzed_at=datetime.datetime.now(datetime.timezone.utc),
    )
    logger.info(
        "Analysis totals file_id=%s income=%s spending=%s",
        file_id,
        result.savings.total_income,
        result.savings.total_spending,
    )
    return result
