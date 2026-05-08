"""
Transactions Endpoint
=====================
GET /transactions/{file_id} — retrieve parsed & categorized transactions
with optional filtering by category, type, and date range.
"""

from typing import List, Optional

from fastapi import APIRouter, HTTPException, Query, status
from pydantic import BaseModel, Field

from app.schemas.category import CategorizedTransaction
from app.services.store import get_results

router = APIRouter()


class TransactionsResponse(BaseModel):
    """Response for transactions list."""

    status: str = "success"
    file_id: str
    total: int
    filtered: int
    transactions: List[CategorizedTransaction]


@router.get(
    "/{file_id}",
    response_model=TransactionsResponse,
    summary="Get categorized transactions",
    description="Returns all parsed and categorized transactions for a file. "
                "Supports filtering by category, type, and date range.",
)
async def get_transactions(
    file_id: str,
    category: Optional[str] = Query(None, description="Filter by category (e.g. food_dining)"),
    type: Optional[str] = Query(None, alias="txn_type", description="Filter: debit | credit"),
    min_amount: Optional[float] = Query(None, ge=0, description="Minimum amount"),
    max_amount: Optional[float] = Query(None, ge=0, description="Maximum amount"),
    date_from: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    date_to: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    sort_by: Optional[str] = Query("date", description="Sort by: date | amount | category"),
    order: Optional[str] = Query("asc", description="Sort order: asc | desc"),
    limit: Optional[int] = Query(None, ge=1, le=500, description="Max results"),
    offset: Optional[int] = Query(0, ge=0, description="Skip N results"),
):
    """
    Retrieve transactions with optional filtering and sorting.
    """
    results = get_results(file_id)
    if not results or not results.categorization_result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No results found for file_id: {file_id}. Upload a file first.",
        )

    txns = list(results.categorization_result.transactions)
    total = len(txns)

    # ── Filters ────────────────────────────────────────────────────────
    if category:
        txns = [t for t in txns if t.category.value == category]

    if type:
        txns = [t for t in txns if t.transaction_type == type]

    if min_amount is not None:
        txns = [t for t in txns if t.amount >= min_amount]

    if max_amount is not None:
        txns = [t for t in txns if t.amount <= max_amount]

    if date_from:
        txns = [
            t for t in txns
            if t.transaction_date and str(t.transaction_date) >= date_from
        ]

    if date_to:
        txns = [
            t for t in txns
            if t.transaction_date and str(t.transaction_date) <= date_to
        ]

    # ── Sort ───────────────────────────────────────────────────────────
    reverse = order == "desc"
    if sort_by == "amount":
        txns.sort(key=lambda t: t.amount, reverse=reverse)
    elif sort_by == "category":
        txns.sort(key=lambda t: t.category.value, reverse=reverse)
    else:  # default: date
        txns.sort(
            key=lambda t: str(t.transaction_date or "9999-99-99"),
            reverse=reverse,
        )

    # ── Pagination ─────────────────────────────────────────────────────
    filtered_count = len(txns)
    if offset:
        txns = txns[offset:]
    if limit:
        txns = txns[:limit]

    return TransactionsResponse(
        file_id=file_id,
        total=total,
        filtered=filtered_count,
        transactions=txns,
    )
