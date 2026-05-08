"""
Profile & Recommendation Schemas
=================================
Financial personality profile, risk assessment, and actionable recommendations.
"""

import datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field


# ═══════════════════════════════════════════════════════════════════════════
# Spending Personality
# ═══════════════════════════════════════════════════════════════════════════

class SpendingPersonality(str, Enum):
    """Financial behavior archetype."""

    FRUGAL = "frugal"
    BALANCED = "balanced"
    COMFORTABLE = "comfortable"
    IMPULSIVE = "impulsive"
    OVERSPENDER = "overspender"


PERSONALITY_DESCRIPTIONS = {
    SpendingPersonality.FRUGAL: (
        "You're a disciplined saver who keeps spending well below income. "
        "You prioritize long-term financial security over short-term gratification."
    ),
    SpendingPersonality.BALANCED: (
        "You maintain a healthy balance between spending and saving. "
        "You enjoy life while being financially responsible."
    ),
    SpendingPersonality.COMFORTABLE: (
        "You spend freely but within your means. "
        "There's room to optimize, but you're not in financial danger."
    ),
    SpendingPersonality.IMPULSIVE: (
        "Your spending patterns suggest frequent unplanned purchases. "
        "Building a budget and waiting 24 hours before non-essential buys could help."
    ),
    SpendingPersonality.OVERSPENDER: (
        "Spending consistently exceeds or matches income. "
        "Immediate action is needed to avoid financial stress."
    ),
}


# ═══════════════════════════════════════════════════════════════════════════
# Risk Level
# ═══════════════════════════════════════════════════════════════════════════

class RiskLevel(str, Enum):
    """Financial risk assessment."""

    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    CRITICAL = "critical"


RISK_DESCRIPTIONS = {
    RiskLevel.LOW: "Your finances are in great shape with healthy margins.",
    RiskLevel.MODERATE: "Some areas need attention, but overall manageable.",
    RiskLevel.HIGH: "Multiple warning signs — action recommended soon.",
    RiskLevel.CRITICAL: "Urgent financial intervention needed.",
}


# ═══════════════════════════════════════════════════════════════════════════
# Recommendations
# ═══════════════════════════════════════════════════════════════════════════

class RecommendationType(str, Enum):
    """Types of recommendations."""

    REDUCE_SPENDING = "reduce_spending"
    CUT_SUBSCRIPTION = "cut_subscription"
    WASTE_DETECTED = "waste_detected"
    ANOMALY_ALERT = "anomaly_alert"
    SAVINGS_TIP = "savings_tip"
    POSITIVE_HABIT = "positive_habit"
    BUDGET_SUGGESTION = "budget_suggestion"


class Recommendation(BaseModel):
    """A single actionable recommendation."""

    type: RecommendationType
    priority: str = Field(..., description="high | medium | low")
    title: str
    description: str
    potential_savings: Optional[float] = Field(
        None, description="Estimated monthly savings if acted upon"
    )
    category: Optional[str] = None
    icon: str = Field("💡", description="Emoji icon for display")


# ═══════════════════════════════════════════════════════════════════════════
# Scores
# ═══════════════════════════════════════════════════════════════════════════

class FinancialScores(BaseModel):
    """Numerical scores across financial dimensions."""

    overall: int = Field(0, ge=0, le=100, description="Overall financial health 0-100")
    savings: int = Field(0, ge=0, le=100, description="Savings discipline 0-100")
    spending_control: int = Field(0, ge=0, le=100, description="Spending control 0-100")
    consistency: int = Field(0, ge=0, le=100, description="Income/spending consistency 0-100")
    diversification: int = Field(0, ge=0, le=100, description="Spending diversification 0-100")


# ═══════════════════════════════════════════════════════════════════════════
# Full Profile
# ═══════════════════════════════════════════════════════════════════════════

class FinancialProfile(BaseModel):
    """Complete financial behavior profile."""

    personality: SpendingPersonality
    personality_description: str
    risk_level: RiskLevel
    risk_description: str
    scores: FinancialScores
    strengths: List[str] = Field(default_factory=list)
    weaknesses: List[str] = Field(default_factory=list)


class ProfileResult(BaseModel):
    """Complete profile + recommendations output."""

    file_id: str
    profile: FinancialProfile
    recommendations: List[Recommendation]
    total_potential_savings: float = 0.0
    generated_at: datetime.datetime


class ProfileResponse(BaseModel):
    """API response wrapper."""

    status: str = "success"
    message: str = "Financial profile generated"
    data: ProfileResult
