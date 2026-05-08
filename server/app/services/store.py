"""
In-Memory Result Store
======================
Caches pipeline results per file_id so GET endpoints can retrieve them
without re-running the pipeline. Will be replaced by DB queries once
PostgreSQL is connected.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Optional

from app.schemas.analysis import AnalysisResult
from app.schemas.category import CategorizationResult
from app.schemas.profile import ProfileResult
from app.schemas.transaction import ParseResult


@dataclass
class FileResults:
    """All pipeline results for a single uploaded file."""

    file_id: str
    original_filename: str
    parse_result: Optional[ParseResult] = None
    categorization_result: Optional[CategorizationResult] = None
    analysis_result: Optional[AnalysisResult] = None
    profile_result: Optional[ProfileResult] = None


# Global in-memory store (keyed by file_id)
_store: Dict[str, FileResults] = {}


def save_results(file_id: str, results: FileResults) -> None:
    """Store pipeline results for a file."""
    _store[file_id] = results


def get_results(file_id: str) -> Optional[FileResults]:
    """Retrieve pipeline results by file_id. Returns None if not found."""
    return _store.get(file_id)


def has_results(file_id: str) -> bool:
    """Check if results exist for a file_id."""
    return file_id in _store


def delete_results(file_id: str) -> None:
    """Remove results for a file_id."""
    _store.pop(file_id, None)


def list_file_ids() -> list[str]:
    """List all file_ids with stored results."""
    return list(_store.keys())
