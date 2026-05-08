"""
Analysis session — temporary server-side storage for one upload/analysis run.
"""

from datetime import datetime, timezone

from sqlalchemy import JSON, DateTime, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.core.config import get_settings
from app.core.database import Base

_settings = get_settings()
_json_type = JSONB if "postgresql" in _settings.DATABASE_URL else JSON


class AnalysisSession(Base):
    """Persisted session payload for dashboard, insights, and transactions."""

    __tablename__ = "analysis_sessions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )
    transactions: Mapped[dict | list] = mapped_column(_json_type, nullable=False)
    insights: Mapped[dict] = mapped_column(_json_type, nullable=False)
    summary: Mapped[dict] = mapped_column(_json_type, nullable=False)
