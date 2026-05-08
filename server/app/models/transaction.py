"""
TransactionRecord Model
=======================
Stores parsed and categorized transactions linked to a file upload.
"""

import uuid
from datetime import date, datetime

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import JSON, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class TransactionRecord(Base):
    __tablename__ = "transactions"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    upload_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("file_uploads.id", ondelete="CASCADE"),
        nullable=False, index=True,
    )

    # Parsed fields
    row_index: Mapped[int] = mapped_column(Integer, nullable=False)
    transaction_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    description: Mapped[str] = mapped_column(Text, default="")
    amount: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    transaction_type: Mapped[str] = mapped_column(
        String(10), nullable=False, default="unknown",
        comment="debit | credit | unknown",
    )

    # Categorization
    category: Mapped[str] = mapped_column(
        String(50), nullable=False, default="other", index=True,
    )
    category_label: Mapped[str] = mapped_column(
        String(100), nullable=False, default="Other",
    )
    categorization_confidence: Mapped[float] = mapped_column(
        Float, default=0.0,
    )
    categorization_method: Mapped[str] = mapped_column(
        String(20), default="keyword", comment="keyword | llm | manual",
    )

    # Metadata
    original_data: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    is_valid: Mapped[bool] = mapped_column(Boolean, default=True)
    validation_notes: Mapped[list | None] = mapped_column(JSON, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    # Relationships
    upload = relationship("FileUpload", back_populates="transactions")

    def __repr__(self) -> str:
        return f"<Transaction row={self.row_index} {self.description[:30]} ₹{self.amount}>"
