"""
File Helpers
============
Utilities for file validation, naming, and temporary storage.
"""

import os
import uuid
from pathlib import Path

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
ALLOWED_EXTENSIONS = {".csv", ".tsv", ".txt", ".xlsx", ".xlsm", ".xls", ".pdf", ".docx", ".doc"}
GENERIC_CONTENT_TYPES = {
    "application/octet-stream",  # fallback — some clients send this
}
CONTENT_TYPES_BY_EXTENSION = {
    ".csv": {
        "text/csv",
        "application/csv",
        "text/comma-separated-values",
    },
    ".tsv": {
        "text/tab-separated-values",
        "text/tsv",
    },
    ".txt": {
        "text/plain",
        "application/plain",
    },
    ".xlsx": {
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "application/vnd.ms-excel",
    },
    ".xlsm": {
        "application/vnd.ms-excel.sheet.macroenabled.12",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    },
    ".xls": {
        "application/vnd.ms-excel",
        "application/excel",
        "application/xls",
        "application/x-excel",
    },
    ".pdf": {
        "application/pdf",
    },
    ".docx": {
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    },
    ".doc": {
        "application/msword",
    },
}
ALLOWED_CONTENT_TYPES = (
    set().union(*CONTENT_TYPES_BY_EXTENSION.values()) | GENERIC_CONTENT_TYPES
)
MAX_FILE_SIZE_MB = 10
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024

# Temp upload directory (relative to server root)
UPLOAD_DIR = Path(__file__).resolve().parent.parent.parent / "uploads"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def ensure_upload_dir() -> Path:
    """Create the upload directory if it doesn't exist."""
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    return UPLOAD_DIR


def generate_file_id() -> str:
    """Generate a unique file identifier."""
    return uuid.uuid4().hex[:16]


def get_file_extension(filename: str) -> str:
    """Extract and normalize the file extension."""
    return Path(filename).suffix.lower()


def validate_file_extension(filename: str) -> bool:
    """Check if the file extension is allowed."""
    return get_file_extension(filename) in ALLOWED_EXTENSIONS


def validate_content_type(content_type: str, filename: str | None = None) -> bool:
    """Check if the MIME type is allowed for the given filename."""
    normalized = (content_type or "").split(";", 1)[0].strip().lower()
    if not normalized:
        return True

    if normalized in GENERIC_CONTENT_TYPES:
        return True

    if normalized in ALLOWED_CONTENT_TYPES:
        return True

    if not filename:
        return False

    ext = get_file_extension(filename)
    if ext in {".csv", ".tsv", ".txt"} and normalized.startswith("text/"):
        return True

    return normalized in CONTENT_TYPES_BY_EXTENSION.get(ext, set())


def humanize_bytes(size_bytes: int) -> str:
    """Convert bytes to a human-readable string."""
    for unit in ("B", "KB", "MB", "GB"):
        if size_bytes < 1024:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f} TB"


def get_file_type_label(filename: str) -> str:
    """Return a clean label for the file type."""
    ext = get_file_extension(filename)
    mapping = {
        ".csv": "csv",
        ".tsv": "tsv",
        ".txt": "txt",
        ".xlsx": "xlsx",
        ".xlsm": "xlsm",
        ".xls": "xls",
        ".pdf": "pdf",
        ".docx": "docx",
        ".doc": "doc",
    }
    return mapping.get(ext, "unknown")


async def save_temp_file(file_id: str, filename: str, contents: bytes) -> str:
    """
    Save uploaded file contents to the temp uploads directory.
    Returns the stored file path.
    """
    upload_dir = ensure_upload_dir()
    ext = get_file_extension(filename)
    stored_name = f"{file_id}{ext}"
    stored_path = upload_dir / stored_name

    with open(stored_path, "wb") as f:
        f.write(contents)

    return str(stored_path)
