"""
AnalysisReport Model
====================
Stores analysis results (trends, profile, recommendations) as JSON
linked to a file upload.
"""

import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import JSON, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class AnalysisReport(Base):
    __tablename__ = "analysis_reports"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    upload_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("file_uploads.id", ondelete="CASCADE"),
        nullable=False, index=True,
    )
    report_type: Mapped[str] = mapped_column(
        String(50), nullable=False, index=True,
        comment="analysis | profile | categorization",
    )

    # Full results stored as JSON
    data: Mapped[dict] = mapped_column(JSON, nullable=False)

    # Summary fields for quick queries
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    # Relationships
    upload = relationship("FileUpload", back_populates="analysis_reports")

    def __repr__(self) -> str:
        return f"<AnalysisReport {self.report_type} for upload={self.upload_id}>"
