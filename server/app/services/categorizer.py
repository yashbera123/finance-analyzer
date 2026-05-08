"""
Transaction Categorizer
=======================
Hybrid categorization engine:
  1. Keyword-based matching (current — high precision, fast)
  2. LLM-based classification (future — plug-in ready)

The `categorize()` function is the single public interface.
Swap the strategy by changing the implementation behind it.
"""

from __future__ import annotations

import logging
import re
from typing import Dict, List, Optional, Tuple

from app.schemas.category import (
    CATEGORY_LABELS,
    CategorizedTransaction,
    CategorizationResult,
    CategorizationSummary,
    Category,
    CategoryBreakdown,
)
from app.schemas.transaction import ParseResult, Transaction, TransactionType

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════════════════
# Keyword rules
# ═══════════════════════════════════════════════════════════════════════════
# Each category maps to a list of lowercase keyword patterns.
# Patterns are checked via substring match against the lowered description.
# More specific patterns come first to avoid false positives.

KEYWORD_RULES: Dict[Category, List[str]] = {
    # ── Food & Dining ─────────────────────────────────────────────────
    Category.FOOD_DINING: [
        "restaurant", "cafe", "coffee", "starbucks", "mcdonald",
        "burger", "pizza", "sushi", "diner", "bistro", "bakery",
        "doordash", "grubhub", "uber eats", "ubereats", "zomato",
        "swiggy", "domino", "kfc", "subway", "chipotle", "taco bell",
        "wendy", "dunkin", "panda express", "food delivery",
        "dining", "eatery", "brunch", "lunch", "dinner",
        "noodle", "ramen", "thai food", "chinese food",
        "ice cream", "dessert", "smoothie", "juice bar",
    ],

    # ── Groceries ─────────────────────────────────────────────────────
    Category.GROCERIES: [
        "grocery", "groceries", "supermarket", "walmart", "target",
        "costco", "kroger", "aldi", "lidl", "whole foods", "wholefoods",
        "trader joe", "safeway", "publix", "wegmans", "heb",
        "fresh market", "food lion", "piggly", "meijer",
        "big bazaar", "dmart", "reliance fresh", "more supermarket",
        "provision", "vegetables", "fruits", "meat shop",
    ],

    # ── Transport ─────────────────────────────────────────────────────
    Category.TRANSPORT: [
        "uber", "lyft", "taxi", "cab", "ola", "grab",
        "gas station", "fuel", "petrol", "diesel", "shell",
        "bp ", "chevron", "exxon", "mobil", "citgo",
        "parking", "toll", "metro", "subway fare", "bus fare",
        "train ticket", "transit", "commute",
        "auto rickshaw", "rapido",
    ],

    # ── Shopping ──────────────────────────────────────────────────────
    Category.SHOPPING: [
        "amazon", "ebay", "flipkart", "myntra", "ajio",
        "shopify", "etsy", "wish.com", "alibaba", "aliexpress",
        "ikea", "home depot", "lowe", "wayfair",
        "best buy", "apple store", "samsung store",
        "zara", "h&m", "uniqlo", "gap", "nike", "adidas",
        "puma", "reebok", "nordstrom", "macy", "tj maxx",
        "marshalls", "ross", "old navy", "primark",
        "online purchase", "online shopping", "shopping", "purchase", "store",
        "clothing", "shoes", "electronics", "furniture",
    ],

    # ── Subscriptions ─────────────────────────────────────────────────
    Category.SUBSCRIPTIONS: [
        "netflix", "spotify", "hulu", "disney+", "disneyplus",
        "hbo", "apple tv", "apple music", "youtube premium",
        "youtube music", "amazon prime", "prime video",
        "audible", "kindle unlimited",
        "adobe", "microsoft 365", "office 365", "google one",
        "dropbox", "icloud", "notion", "figma", "canva",
        "github", "gitlab", "slack", "zoom",
        "subscription", "recurring", "membership",
        "patreon", "substack", "medium",
        "crunchyroll", "paramount", "peacock",
        "chatgpt", "openai", "copilot",
    ],

    # ── Bills & Utilities ─────────────────────────────────────────────
    Category.BILLS_UTILITIES: [
        "electric bill", "electricity", "power bill",
        "water bill", "gas bill", "utility",
        "internet", "wifi", "broadband", "fiber",
        "phone bill", "mobile bill", "cell phone",
        "at&t", "verizon", "t-mobile", "tmobile", "sprint",
        "comcast", "xfinity", "spectrum", "cox",
        "jio", "airtel", "vodafone", "bsnl",
        "sewage", "trash", "waste management",
    ],

    # ── Rent & Housing ────────────────────────────────────────────────
    Category.RENT_HOUSING: [
        "rent", "lease", "mortgage", "home loan", "emi",
        "property tax", "hoa", "maintenance fee",
        "real estate", "apartment", "housing",
        "landlord", "tenant",
    ],

    # ── Health & Fitness ──────────────────────────────────────────────
    Category.HEALTH_FITNESS: [
        "gym", "fitness", "yoga", "pilates", "crossfit",
        "peloton", "planet fitness", "anytime fitness",
        "pharmacy", "cvs", "walgreens", "rite aid",
        "hospital", "clinic", "doctor", "dentist",
        "medical", "health", "therapy", "therapist",
        "prescription", "medicine", "lab test",
        "optical", "eye care", "vision",
    ],

    # ── Entertainment ─────────────────────────────────────────────────
    Category.ENTERTAINMENT: [
        "movie", "cinema", "theater", "theatre", "concert",
        "ticket", "event", "show", "amusement", "theme park",
        "bowling", "arcade", "gaming", "game", "steam",
        "playstation", "xbox", "nintendo",
        "museum", "gallery", "zoo", "aquarium",
        "bar", "pub", "club", "lounge", "nightclub",
        "karaoke", "billiards", "pool hall",
    ],

    # ── Travel ────────────────────────────────────────────────────────
    Category.TRAVEL: [
        "flight", "airline", "airways", "air ticket",
        "hotel", "motel", "hostel", "airbnb", "booking.com",
        "expedia", "trivago", "kayak", "priceline",
        "resort", "vacation", "travel", "trip",
        "luggage", "passport", "visa fee",
        "car rental", "hertz", "enterprise", "avis",
        "cruise", "tour",
    ],

    # ── Education ─────────────────────────────────────────────────────
    Category.EDUCATION: [
        "tuition", "university", "college", "school",
        "course", "udemy", "coursera", "skillshare",
        "textbook", "book store", "bookstore",
        "education", "learning", "training", "workshop",
        "certification", "exam fee", "tutorial",
        "masterclass", "linkedin learning",
    ],

    # ── Income ────────────────────────────────────────────────────────
    Category.INCOME: [
        "salary", "payroll", "paycheck", "wage",
        "freelance", "consulting", "commission",
        "dividend", "interest earned", "interest income",
        "refund", "reimbursement", "cashback", "cash back",
        "bonus", "incentive", "stipend",
        "deposit", "income",
        "rental income", "side hustle",
    ],

    # ── Transfer ──────────────────────────────────────────────────────
    Category.TRANSFER: [
        "transfer", "wire transfer", "bank transfer",
        "zelle", "venmo", "paypal", "cashapp", "cash app",
        "gpay", "google pay", "apple pay",
        "neft", "rtgs", "imps", "upi",
        "sent to", "received from",
        "internal transfer", "self transfer",
    ],

    # ── ATM & Cash ────────────────────────────────────────────────────
    Category.ATM_CASH: [
        "atm", "cash withdrawal", "cash deposit",
        "withdraw", "withdrawal",
        "cashback at", "cash advance",
    ],

    # ── Insurance ─────────────────────────────────────────────────────
    Category.INSURANCE: [
        "insurance", "premium", "life insurance",
        "health insurance", "auto insurance", "car insurance",
        "home insurance", "renters insurance",
        "geico", "progressive", "state farm", "allstate",
        "policy", "coverage",
    ],

    # ── Investments ───────────────────────────────────────────────────
    Category.INVESTMENTS: [
        "investment", "stock", "mutual fund", "etf",
        "trading", "brokerage", "robinhood", "fidelity",
        "vanguard", "schwab", "td ameritrade",
        "crypto", "bitcoin", "ethereum", "coinbase",
        "binance", "sip", "ppf", "nps",
        "401k", "ira", "roth",
    ],

    # ── Personal Care ─────────────────────────────────────────────────
    Category.PERSONAL_CARE: [
        "salon", "barber", "haircut", "spa",
        "beauty", "cosmetic", "skincare", "makeup",
        "nail", "manicure", "pedicure",
        "sephora", "ulta", "bath & body",
        "grooming", "self care",
    ],

    # ── Gifts & Donations ────────────────────────────────────────────
    Category.GIFTS_DONATIONS: [
        "gift", "donation", "charity", "nonprofit",
        "gofundme", "fundraiser", "tithe",
        "birthday present", "wedding gift",
        "contribution",
    ],

    # ── Fees & Charges ────────────────────────────────────────────────
    Category.FEES_CHARGES: [
        "fee", "charge", "penalty", "fine",
        "overdraft", "nsf", "late fee", "service charge",
        "annual fee", "maintenance charge",
        "interest charge", "finance charge",
        "bank fee", "atm fee", "foreign transaction",
    ],
}


# ═══════════════════════════════════════════════════════════════════════════
# Keyword matching engine
# ═══════════════════════════════════════════════════════════════════════════

def _keyword_classify(description: str) -> Tuple[Category, float]:
    """
    Match a transaction description against keyword rules.

    Returns (category, confidence).
    Confidence is 1.0 for exact keyword hits, 0.0 for no match.
    """
    if not description:
        return Category.OTHER, 0.0

    desc_lower = description.lower()

    best_category = Category.OTHER
    best_score = 0  # number of keyword hits (more hits = better match)

    for category, keywords in KEYWORD_RULES.items():
        score = 0
        for kw in keywords:
            if kw in desc_lower:
                # Longer keyword matches are weighted higher
                score += len(kw)

        if score > best_score:
            best_score = score
            best_category = category

    if best_score > 0:
        # Confidence scales with match quality, capped at 1.0
        confidence = min(best_score / 10.0, 1.0)
        return best_category, round(confidence, 2)

    return Category.OTHER, 0.0


# ═══════════════════════════════════════════════════════════════════════════
# Smart fallback — transaction type hints
# ═══════════════════════════════════════════════════════════════════════════

def _type_based_fallback(
    txn_type: str, category: Category
) -> Tuple[Category, float]:
    """
    If keyword matching returned OTHER, apply type-based heuristics.
    Credits without a keyword match are likely income.
    """
    if category != Category.OTHER:
        return category, 0.0  # no change needed

    if txn_type == "credit":
        return Category.INCOME, 0.3
    return Category.OTHER, 0.0


# ═══════════════════════════════════════════════════════════════════════════
# Public interface
# ═══════════════════════════════════════════════════════════════════════════

def categorize_transaction(
    description: str,
    txn_type: str = "unknown",
    method: str = "keyword",
) -> Tuple[Category, str, float, str]:
    """
    Categorize a single transaction.

    Returns: (category, label, confidence, method)

    This is the function to replace with LLM calls in a future phase.
    The interface stays the same — only the internals change.
    """
    if method == "keyword":
        category, confidence = _keyword_classify(description)

        # Apply fallback if uncategorized
        if category == Category.OTHER:
            fb_category, fb_confidence = _type_based_fallback(txn_type, category)
            if fb_category != Category.OTHER:
                category = fb_category
                confidence = fb_confidence

        label = CATEGORY_LABELS[category]
        return category, label, confidence, "keyword"

    # ── Future: LLM method ─────────────────────────────────────────────
    # elif method == "llm":
    #     return _llm_classify(description)

    return Category.OTHER, CATEGORY_LABELS[Category.OTHER], 0.0, method


def categorize_transactions(parse_result: ParseResult) -> CategorizationResult:
    """
    Categorize all transactions from a ParseResult.

    Returns a CategorizationResult with:
    - categorized transactions
    - category breakdown
    - summary statistics
    """
    valid_transactions = [txn for txn in parse_result.transactions if txn.is_valid]
    logger.info(
        "Categorization input file_id=%s valid_transactions=%d raw_transactions=%d",
        parse_result.file_id,
        len(valid_transactions),
        len(parse_result.transactions),
    )

    categorized: List[CategorizedTransaction] = []

    for txn in valid_transactions:
        category, label, confidence, method = categorize_transaction(
            description=txn.description,
            txn_type=txn.transaction_type.value,
        )

        categorized.append(
            CategorizedTransaction(
                row_index=txn.row_index,
                transaction_date=txn.transaction_date,
                description=txn.description,
                amount=txn.amount,
                transaction_type=txn.transaction_type.value,
                category=category,
                category_label=label,
                confidence=confidence,
                method=method,
            )
        )

    # ── Build breakdown ────────────────────────────────────────────────
    breakdown_map: Dict[Category, CategoryBreakdown] = {}

    total_spending = 0.0
    total_income = 0.0

    for ct in categorized:
        cat = ct.category

        if cat not in breakdown_map:
            breakdown_map[cat] = CategoryBreakdown(
                category=cat,
                label=CATEGORY_LABELS[cat],
            )

        breakdown_map[cat].total_amount = round(
            breakdown_map[cat].total_amount + ct.amount, 2
        )
        breakdown_map[cat].transaction_count += 1

        if ct.transaction_type == "debit":
            total_spending += ct.amount
        elif ct.transaction_type == "credit":
            total_income += ct.amount

    # Calculate percentages (based on spending only)
    if total_spending > 0:
        for bd in breakdown_map.values():
            # Only calculate % for non-income categories
            if bd.category != Category.INCOME:
                bd.percentage = round(
                    (bd.total_amount / total_spending) * 100, 1
                )

    # Sort by total amount descending
    breakdown = sorted(
        breakdown_map.values(),
        key=lambda b: b.total_amount,
        reverse=True,
    )

    # Top spending category (exclude income/transfer)
    spending_categories = [
        b for b in breakdown
        if b.category not in (Category.INCOME, Category.TRANSFER)
    ]
    top_category = spending_categories[0].label if spending_categories else None

    categorized_count = sum(1 for c in categorized if c.category != Category.OTHER)

    summary = CategorizationSummary(
        total_transactions=len(categorized),
        categorized_count=categorized_count,
        uncategorized_count=len(categorized) - categorized_count,
        category_breakdown=breakdown,
        top_category=top_category,
        total_spending=round(total_spending, 2),
        total_income=round(total_income, 2),
    )

    return CategorizationResult(
        file_id=parse_result.file_id,
        summary=summary,
        transactions=categorized,
    )
