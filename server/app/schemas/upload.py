"""
Upload Schemas
==============
Request/response models for the file upload endpoint.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class FileMetadata(BaseModel):
    """Metadata returned after a successful file upload."""

    file_id: str = Field(..., description="Unique identifier for the uploaded file")
    session_id: str = Field(..., description="Server session id for GET /session/{session_id}")
    original_filename: str = Field(..., description="Original name of the uploaded file")
    file_type: str = Field(
        ...,
        description="Detected file type (csv / tsv / txt / xlsx / xlsm / xls)",
    )
    file_size_bytes: int = Field(..., description="File size in bytes")
    file_size_human: str = Field(..., description="Human-readable file size")
    stored_path: str = Field(..., description="Server-side storage path")
    uploaded_at: datetime = Field(..., description="Timestamp of upload")


class UploadResponse(BaseModel):
    """Response for POST /upload."""

    status: str = "success"
    message: str = "File uploaded successfully"
    data: FileMetadata


class UploadErrorResponse(BaseModel):
    """Error response for upload failures."""

    status: str = "error"
    message: str
    detail: Optional[str] = None
