"""
Categorize Endpoint
===================
POST /categorize/{file_id} — parses a previously uploaded file, then
categorizes all transactions using keyword matching.
"""

from fastapi import APIRouter, HTTPException, status

from app.schemas.category import CategorizationResponse
from app.services.categorizer import categorize_transactions
from app.services.parser import parse_transactions, validate_parse_result
from app.utils.file_helpers import UPLOAD_DIR

from pathlib import Path

router = APIRouter()


def _find_uploaded_file(file_id: str) -> Path:
    """Locate an uploaded file by its ID."""
    upload_dir = Path(UPLOAD_DIR)
    if not upload_dir.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Upload directory not found.",
        )
    matches = list(upload_dir.glob(f"{file_id}.*"))
    if not matches:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No uploaded file found for file_id: {file_id}",
        )
    return matches[0]


@router.post(
    "/{file_id}",
    response_model=CategorizationResponse,
    summary="Categorize transactions from an uploaded file",
    description="Parses the file and categorizes each transaction "
                "using keyword matching. Returns categorized transactions "
                "with a spending breakdown.",
)
async def categorize_file(file_id: str):
    """
    Parse + categorize a previously uploaded file.

    Pipeline:
    1. Locate file by file_id
    2. Parse into structured transactions
    3. Categorize each transaction
    4. Return results with breakdown
    """
    file_path = _find_uploaded_file(file_id)

    # Parse
    try:
        parse_result = parse_transactions(
            file_path=str(file_path),
            file_id=file_id,
            original_filename=file_path.name,
        )
        validate_parse_result(parse_result)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Failed to parse file: {str(e)}",
        )

    # Categorize
    try:
        result = categorize_transactions(parse_result)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Categorization failed: {str(e)}",
        )

    return CategorizationResponse(
        status="success",
        message=f"Categorized {result.summary.categorized_count} of "
                f"{result.summary.total_transactions} transactions",
        data=result,
    )
