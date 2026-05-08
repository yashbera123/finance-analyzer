"""
Transaction Schemas
===================
Standardized transaction models used across the entire application.
"""

import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class TransactionType(str, Enum):
    """Direction of money flow."""
    DEBIT = "debit"
    CREDIT = "credit"
    UNKNOWN = "unknown"


class Transaction(BaseModel):
    """A single normalized transaction."""

    model_config = {"populate_by_name": True, "serialize_by_alias": True}

    row_index: int = Field(..., description="Original row number in the source file")
    transaction_date: Optional[datetime.date] = Field(None, alias="date", description="Transaction date (ISO format)")
    description: str = Field("", description="Cleaned transaction description")
    amount: float = Field(0.0, description="Absolute transaction amount")
    transaction_type: TransactionType = Field(
        TransactionType.UNKNOWN, description="Debit or credit"
    )
    original_data: dict = Field(
        default_factory=dict,
        description="Raw row data before normalization (for debugging)",
    )
    is_valid: bool = Field(True, description="Whether this row passed basic validation")
    validation_notes: List[str] = Field(
        default_factory=list, description="Any issues found during parsing"
    )


class ColumnMapping(BaseModel):
    """Detected column mapping from the source file."""

    date_column: Optional[str] = None
    description_column: Optional[str] = None
    amount_column: Optional[str] = None
    debit_column: Optional[str] = None
    credit_column: Optional[str] = None
    type_column: Optional[str] = None
    confidence: float = Field(0.0, description="Overall mapping confidence 0-1")


class ParseSummary(BaseModel):
    """Summary statistics for a parse operation."""

    total_rows: int = 0
    valid_rows: int = 0
    invalid_rows: int = 0
    skipped_rows: int = 0
    date_range_start: Optional[datetime.date] = None
    date_range_end: Optional[datetime.date] = None
    total_debits: float = 0.0
    total_credits: float = 0.0
    net_amount: float = 0.0


class ParseResult(BaseModel):
    """Complete result from parsing a financial file."""

    file_id: str
    original_filename: str
    column_mapping: ColumnMapping
    summary: ParseSummary
    transactions: List[Transaction]


class ParseResponse(BaseModel):
    """API response wrapper for parse results."""

    status: str = "success"
    message: str = "File parsed successfully"
    data: ParseResult


class ColumnCorrectionRequest(BaseModel):
    """Request to correct column mappings."""

    date_column: Optional[str] = None
    description_column: Optional[str] = None
    amount_column: Optional[str] = None
    debit_column: Optional[str] = None
    credit_column: Optional[str] = None
    type_column: Optional[str] = None


class CorrectionNeededResponse(BaseModel):
    """Response when column mapping needs user correction."""

    status: str = "correction_needed"
    message: str = "Column mapping requires user confirmation"
    data: dict  # Contains detected_columns, sample_data, etc.
