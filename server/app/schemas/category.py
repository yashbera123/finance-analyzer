"""
Category Schemas
================
Category definitions and categorized transaction models.
"""

import datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field


class Category(str, Enum):
    """Spending categories."""

    FOOD_DINING = "food_dining"
    GROCERIES = "groceries"
    TRANSPORT = "transport"
    SHOPPING = "shopping"
    SUBSCRIPTIONS = "subscriptions"
    BILLS_UTILITIES = "bills_utilities"
    RENT_HOUSING = "rent_housing"
    HEALTH_FITNESS = "health_fitness"
    ENTERTAINMENT = "entertainment"
    TRAVEL = "travel"
    EDUCATION = "education"
    INCOME = "income"
    TRANSFER = "transfer"
    ATM_CASH = "atm_cash"
    INSURANCE = "insurance"
    INVESTMENTS = "investments"
    PERSONAL_CARE = "personal_care"
    GIFTS_DONATIONS = "gifts_donations"
    FEES_CHARGES = "fees_charges"
    OTHER = "other"


# Human-readable display names
CATEGORY_LABELS = {
    Category.FOOD_DINING: "Food & Dining",
    Category.GROCERIES: "Groceries",
    Category.TRANSPORT: "Transport",
    Category.SHOPPING: "Shopping",
    Category.SUBSCRIPTIONS: "Subscriptions",
    Category.BILLS_UTILITIES: "Bills & Utilities",
    Category.RENT_HOUSING: "Rent & Housing",
    Category.HEALTH_FITNESS: "Health & Fitness",
    Category.ENTERTAINMENT: "Entertainment",
    Category.TRAVEL: "Travel",
    Category.EDUCATION: "Education",
    Category.INCOME: "Income",
    Category.TRANSFER: "Transfer",
    Category.ATM_CASH: "ATM & Cash",
    Category.INSURANCE: "Insurance",
    Category.INVESTMENTS: "Investments",
    Category.PERSONAL_CARE: "Personal Care",
    Category.GIFTS_DONATIONS: "Gifts & Donations",
    Category.FEES_CHARGES: "Fees & Charges",
    Category.OTHER: "Other",
}


class CategorizedTransaction(BaseModel):
    """A transaction with its assigned category."""

    row_index: int
    transaction_date: Optional[datetime.date] = Field(None, alias="date")
    description: str = ""
    amount: float = 0.0
    transaction_type: str = "unknown"
    category: Category = Category.OTHER
    category_label: str = "Other"
    confidence: float = Field(
        0.0, description="Categorization confidence 0-1 (1.0 = keyword match)"
    )
    method: str = Field(
        "keyword", description="Categorization method: keyword | llm | manual"
    )

    model_config = {"populate_by_name": True, "serialize_by_alias": True}


class CategoryBreakdown(BaseModel):
    """Spending breakdown for a single category."""

    category: Category
    label: str
    total_amount: float = 0.0
    transaction_count: int = 0
    percentage: float = 0.0


class CategorizationSummary(BaseModel):
    """Summary of categorization results."""

    total_transactions: int = 0
    categorized_count: int = 0
    uncategorized_count: int = 0
    category_breakdown: List[CategoryBreakdown] = Field(default_factory=list)
    top_category: Optional[str] = None
    total_spending: float = 0.0
    total_income: float = 0.0


class CategorizationResult(BaseModel):
    """Complete result from categorizing transactions."""

    file_id: str
    summary: CategorizationSummary
    transactions: List[CategorizedTransaction]


class CategorizationResponse(BaseModel):
    """API response wrapper."""

    status: str = "success"
    message: str = "Transactions categorized successfully"
    data: CategorizationResult
