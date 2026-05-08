"""
Financial Profiler & Recommendation Engine
============================================
Consumes analysis results (Phase 5) and produces:
  1. Spending personality classification
  2. Risk level assessment
  3. Financial health scores (5 dimensions)
  4. Strengths & weaknesses
  5. Actionable recommendations

Each concern is a standalone function — easy to extend or override.
"""

from __future__ import annotations

import datetime
from typing import List, Tuple

from app.schemas.analysis import AnalysisResult
from app.schemas.profile import (
    PERSONALITY_DESCRIPTIONS,
    RISK_DESCRIPTIONS,
    FinancialProfile,
    FinancialScores,
    ProfileResult,
    Recommendation,
    RecommendationType,
    RiskLevel,
    SpendingPersonality,
)


# ═══════════════════════════════════════════════════════════════════════════
# 1. Spending Personality
# ═══════════════════════════════════════════════════════════════════════════

def classify_personality(analysis: AnalysisResult) -> SpendingPersonality:
    """
    Classify spending personality based on savings ratio,
    spending trends, and recurring patterns.
    """
    savings = analysis.savings
    ratio = savings.savings_ratio

    # Factor in trend direction
    trend = analysis.trends.spending_trend
    recurring_pct = 0.0
    if savings.total_spending > 0:
        recurring_pct = (
            analysis.recurring.estimated_monthly_recurring / savings.total_spending
        ) * 100

    # Impulsive indicators: low recurring %, high anomaly rate, increasing trend
    anomaly_rate = analysis.anomalies.anomaly_rate
    is_impulsive = (
        anomaly_rate > 15
        or (trend == "increasing" and ratio < 15)
        or (recurring_pct < 30 and ratio < 20)
    )

    if ratio >= 40:
        return SpendingPersonality.FRUGAL
    elif ratio >= 20:
        if is_impulsive:
            return SpendingPersonality.IMPULSIVE
        return SpendingPersonality.BALANCED
    elif ratio >= 10:
        if is_impulsive:
            return SpendingPersonality.IMPULSIVE
        return SpendingPersonality.COMFORTABLE
    elif ratio >= 0:
        return SpendingPersonality.IMPULSIVE
    else:
        return SpendingPersonality.OVERSPENDER


# ═══════════════════════════════════════════════════════════════════════════
# 2. Risk Level
# ═══════════════════════════════════════════════════════════════════════════

def assess_risk(analysis: AnalysisResult) -> RiskLevel:
    """
    Assess financial risk level based on multiple signals.
    """
    risk_score = 0

    savings = analysis.savings

    # Savings ratio risk
    if savings.savings_ratio < 0:
        risk_score += 4
    elif savings.savings_ratio < 10:
        risk_score += 3
    elif savings.savings_ratio < 20:
        risk_score += 1

    # Spending trend risk
    if analysis.trends.spending_trend == "increasing":
        risk_score += 2

    # Anomaly rate risk
    if analysis.anomalies.anomaly_rate > 20:
        risk_score += 2
    elif analysis.anomalies.anomaly_rate > 10:
        risk_score += 1

    # High recurring commitment risk
    if savings.total_spending > 0:
        recurring_pct = (
            analysis.recurring.estimated_monthly_recurring / savings.total_spending
        ) * 100
        if recurring_pct > 80:
            risk_score += 2
        elif recurring_pct > 60:
            risk_score += 1

    # Single category dominance risk (>50% in one category)
    if analysis.categories.breakdown:
        top_pct = analysis.categories.breakdown[0].percentage
        if top_pct > 50:
            risk_score += 1

    # Map score to level
    if risk_score >= 7:
        return RiskLevel.CRITICAL
    elif risk_score >= 4:
        return RiskLevel.HIGH
    elif risk_score >= 2:
        return RiskLevel.MODERATE
    else:
        return RiskLevel.LOW


# ═══════════════════════════════════════════════════════════════════════════
# 3. Financial Scores
# ═══════════════════════════════════════════════════════════════════════════

def compute_scores(analysis: AnalysisResult) -> FinancialScores:
    """
    Compute financial health scores (0-100) across five dimensions.
    """
    savings = analysis.savings

    # ── Savings score ──────────────────────────────────────────────────
    # 50% ratio → 100, 0% → 30, negative → 0-20
    if savings.savings_ratio >= 50:
        savings_score = 100
    elif savings.savings_ratio >= 0:
        savings_score = int(30 + (savings.savings_ratio / 50) * 70)
    else:
        savings_score = max(0, int(20 + savings.savings_ratio))

    # ── Spending control ───────────────────────────────────────────────
    # Based on anomaly rate and trend stability
    control_score = 80
    if analysis.trends.spending_trend == "increasing":
        control_score -= 20
    elif analysis.trends.spending_trend == "decreasing":
        control_score += 10
    control_score -= int(analysis.anomalies.anomaly_rate * 2)
    control_score = max(0, min(100, control_score))

    # ── Consistency ────────────────────────────────────────────────────
    # How stable is monthly spending? Low variance = high consistency
    months = analysis.trends.months
    if len(months) >= 2:
        spending_values = [m.total_spending for m in months if m.total_spending > 0]
        if spending_values:
            avg = sum(spending_values) / len(spending_values)
            variance = sum((v - avg) ** 2 for v in spending_values) / len(spending_values)
            std = variance ** 0.5
            cv = (std / avg) * 100 if avg > 0 else 100  # coefficient of variation
            consistency_score = max(0, min(100, int(100 - cv * 2)))
        else:
            consistency_score = 50
    else:
        consistency_score = 50  # not enough data

    # ── Diversification ────────────────────────────────────────────────
    # More categories = better diversification; heavy concentration = worse
    num_categories = analysis.categories.total_categories_used
    if analysis.categories.breakdown:
        top_pct = analysis.categories.breakdown[0].percentage
    else:
        top_pct = 100
    diversification_score = min(100, max(0, int(
        (num_categories * 10) + (100 - top_pct) * 0.5
    )))

    # ── Overall ────────────────────────────────────────────────────────
    overall = int(
        savings_score * 0.35
        + control_score * 0.25
        + consistency_score * 0.20
        + diversification_score * 0.20
    )

    return FinancialScores(
        overall=max(0, min(100, overall)),
        savings=max(0, min(100, savings_score)),
        spending_control=max(0, min(100, control_score)),
        consistency=max(0, min(100, consistency_score)),
        diversification=max(0, min(100, diversification_score)),
    )


# ═══════════════════════════════════════════════════════════════════════════
# 4. Strengths & Weaknesses
# ═══════════════════════════════════════════════════════════════════════════

def identify_strengths_weaknesses(
    analysis: AnalysisResult,
    scores: FinancialScores,
) -> Tuple[List[str], List[str]]:
    """Identify top strengths and weaknesses from analysis data."""

    strengths: List[str] = []
    weaknesses: List[str] = []

    # Savings
    if analysis.savings.savings_ratio >= 30:
        strengths.append(f"Excellent savings rate of {analysis.savings.savings_ratio}%")
    elif analysis.savings.savings_ratio >= 20:
        strengths.append(f"Healthy savings rate of {analysis.savings.savings_ratio}%")
    elif analysis.savings.savings_ratio < 10:
        weaknesses.append(f"Low savings rate of {analysis.savings.savings_ratio}%")

    # Spending trend
    if analysis.trends.spending_trend == "decreasing":
        strengths.append("Spending is trending downward — great discipline")
    elif analysis.trends.spending_trend == "increasing":
        weaknesses.append("Spending is trending upward month over month")

    # Recurring management
    subs = [r for r in analysis.recurring.recurring_transactions if r.is_subscription]
    if len(subs) <= 3:
        strengths.append("Subscription count is well-managed")
    elif len(subs) >= 6:
        weaknesses.append(f"{len(subs)} active subscriptions — review for unused ones")

    # Anomalies
    if analysis.anomalies.anomaly_rate <= 5:
        strengths.append("Very consistent spending patterns")
    elif analysis.anomalies.anomaly_rate > 15:
        weaknesses.append("High rate of unusual transactions")

    # Category concentration
    if analysis.categories.breakdown:
        top = analysis.categories.breakdown[0]
        if top.percentage > 50:
            weaknesses.append(
                f"{top.label} accounts for {top.percentage}% of spending — high concentration"
            )
        elif analysis.categories.total_categories_used >= 5:
            strengths.append("Well-diversified spending across categories")

    # Consistency
    if scores.consistency >= 70:
        strengths.append("Consistent monthly spending — predictable and manageable")
    elif scores.consistency < 40:
        weaknesses.append("High month-to-month spending variance")

    return strengths[:5], weaknesses[:5]


# ═══════════════════════════════════════════════════════════════════════════
# 5. Recommendations
# ═══════════════════════════════════════════════════════════════════════════

def generate_recommendations(analysis: AnalysisResult) -> List[Recommendation]:
    """
    Generate actionable recommendations based on analysis results.
    """
    recs: List[Recommendation] = []

    # ── Category reduction suggestions ─────────────────────────────────
    for cat in analysis.categories.breakdown[:5]:
        if cat.percentage >= 30 and cat.category not in ("rent_housing", "income"):
            recs.append(Recommendation(
                type=RecommendationType.REDUCE_SPENDING,
                priority="high",
                title=f"Reduce {cat.label} spending",
                description=(
                    f"{cat.label} accounts for {cat.percentage}% of total spending "
                    f"(₹{cat.total:,.2f}). Target a 15% reduction for meaningful savings."
                ),
                potential_savings=round(cat.total * 0.15, 2),
                category=cat.label,
                icon="📉",
            ))
        elif cat.percentage >= 15 and cat.category not in ("rent_housing", "income"):
            recs.append(Recommendation(
                type=RecommendationType.BUDGET_SUGGESTION,
                priority="medium",
                title=f"Set a budget for {cat.label}",
                description=(
                    f"{cat.label} is {cat.percentage}% of spending. "
                    f"Setting a monthly budget of ₹{cat.total * 0.85:,.2f} could help."
                ),
                potential_savings=round(cat.total * 0.10, 2),
                category=cat.label,
                icon="📊",
            ))

    # ── Subscription audit ─────────────────────────────────────────────
    subs = [r for r in analysis.recurring.recurring_transactions if r.is_subscription]
    if len(subs) >= 3:
        total_sub_cost = sum(s.amount for s in subs)
        recs.append(Recommendation(
            type=RecommendationType.CUT_SUBSCRIPTION,
            priority="medium",
            title="Audit your subscriptions",
            description=(
                f"You have {len(subs)} active subscriptions totaling "
                f"~₹{total_sub_cost:,.2f}/month. Review each for usage — "
                f"cutting 1-2 unused services could save significantly."
            ),
            potential_savings=round(total_sub_cost * 0.3, 2),
            icon="✂️",
        ))

    # ── Waste detection: small frequent purchases ──────────────────────
    food_cat = next(
        (c for c in analysis.categories.breakdown if c.category == "food_dining"),
        None,
    )
    if food_cat and food_cat.count >= 5:
        avg = food_cat.avg_per_transaction
        recs.append(Recommendation(
            type=RecommendationType.WASTE_DETECTED,
            priority="medium",
            title="Frequent dining/coffee spending detected",
            description=(
                f"{food_cat.count} food & dining transactions averaging "
                f"₹{avg:,.2f} each. Small daily purchases add up — "
                f"preparing meals at home 2-3 extra days/week could save "
                f"₹{avg * 8:,.2f}/month."
            ),
            potential_savings=round(avg * 8, 2),
            category="Food & Dining",
            icon="☕",
        ))

    # ── Anomaly alerts ─────────────────────────────────────────────────
    for anomaly in analysis.anomalies.anomalies[:3]:  # Top 3 most anomalous
        recs.append(Recommendation(
            type=RecommendationType.ANOMALY_ALERT,
            priority="high" if anomaly.amount > 500 else "medium",
            title=f"Unusual transaction: {anomaly.description}",
            description=(
                f"₹{anomaly.amount:,.2f} on {anomaly.transaction_date or 'unknown date'} — "
                f"{anomaly.reason}. Verify this is intentional."
            ),
            category=anomaly.category,
            icon="⚠️",
        ))

    # ── Savings tips ───────────────────────────────────────────────────
    savings = analysis.savings
    if savings.savings_ratio < 20 and savings.total_income > 0:
        target = round(savings.total_income * 0.20, 2)
        gap = round(target - savings.net_savings, 2)
        if gap > 0:
            recs.append(Recommendation(
                type=RecommendationType.SAVINGS_TIP,
                priority="high",
                title="Build towards 20% savings rate",
                description=(
                    f"Your current savings rate is {savings.savings_ratio}%. "
                    f"To reach 20%, reduce monthly spending by ~₹{gap:,.2f}. "
                    f"Start with the highest-impact categories above."
                ),
                potential_savings=gap,
                icon="🎯",
            ))

    # ── Positive habits ────────────────────────────────────────────────
    if savings.savings_ratio >= 25:
        recs.append(Recommendation(
            type=RecommendationType.POSITIVE_HABIT,
            priority="low",
            title="Great savings discipline!",
            description=(
                f"You're saving {savings.savings_ratio}% of income. "
                f"Consider putting surplus into investments or an emergency fund "
                f"for even greater financial security."
            ),
            icon="🌟",
        ))

    if analysis.trends.spending_trend == "decreasing":
        recs.append(Recommendation(
            type=RecommendationType.POSITIVE_HABIT,
            priority="low",
            title="Spending is decreasing — keep it up!",
            description=(
                "Your month-over-month spending is trending downward. "
                "This discipline will compound over time."
            ),
            icon="📈",
        ))

    # Sort: high priority first
    priority_order = {"high": 0, "medium": 1, "low": 2}
    recs.sort(key=lambda r: priority_order.get(r.priority, 1))

    return recs


# ═══════════════════════════════════════════════════════════════════════════
# Orchestrator
# ═══════════════════════════════════════════════════════════════════════════

def generate_profile(
    file_id: str,
    analysis: AnalysisResult,
) -> ProfileResult:
    """
    Generate the complete financial profile and recommendations
    from analysis results.
    """
    personality = classify_personality(analysis)
    risk = assess_risk(analysis)
    scores = compute_scores(analysis)
    strengths, weaknesses = identify_strengths_weaknesses(analysis, scores)
    recommendations = generate_recommendations(analysis)

    total_potential_savings = round(
        sum(r.potential_savings for r in recommendations if r.potential_savings), 2
    )

    profile = FinancialProfile(
        personality=personality,
        personality_description=PERSONALITY_DESCRIPTIONS[personality],
        risk_level=risk,
        risk_description=RISK_DESCRIPTIONS[risk],
        scores=scores,
        strengths=strengths,
        weaknesses=weaknesses,
    )

    return ProfileResult(
        file_id=file_id,
        profile=profile,
        recommendations=recommendations,
        total_potential_savings=total_potential_savings,
        generated_at=datetime.datetime.now(datetime.timezone.utc),
    )
