"""
FileUpload Model
================
Tracks uploaded financial data files and links to parsed transactions.
"""

import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class FileUpload(Base):
    __tablename__ = "file_uploads"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    file_id: Mapped[str] = mapped_column(
        String(32), unique=True, index=True, nullable=False,
        comment="Short hex ID used in API URLs",
    )
    user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=True,
    )
    original_filename: Mapped[str] = mapped_column(String(500), nullable=False)
    file_type: Mapped[str] = mapped_column(String(10), nullable=False)
    file_size_bytes: Mapped[int] = mapped_column(Integer, nullable=False)
    stored_path: Mapped[str] = mapped_column(String(1000), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    # Relationships
    user = relationship("User", back_populates="uploads")
    transactions = relationship(
        "TransactionRecord", back_populates="upload", lazy="selectin",
        cascade="all, delete-orphan",
    )
    analysis_reports = relationship(
        "AnalysisReport", back_populates="upload", lazy="selectin",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<FileUpload {self.file_id}: {self.original_filename}>"
