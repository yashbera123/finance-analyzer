"""
Parse Endpoint
==============
POST /parse — takes a file_id from a previous upload, runs the parsing
engine, and returns structured transaction data.
"""

from pathlib import Path

from fastapi import APIRouter, HTTPException, status

from app.schemas.transaction import (
    ColumnMapping,
    ParseResponse,
    CorrectionNeededResponse,
    ColumnCorrectionRequest,
)
from app.services.parser import parse_transactions, read_file_to_dataframe, parse_transactions_with_mapping
from app.utils.file_helpers import UPLOAD_DIR

router = APIRouter()


def _find_uploaded_file(file_id: str) -> Path:
    """Locate an uploaded file by its ID in the uploads directory."""
    upload_dir = Path(UPLOAD_DIR)
    if not upload_dir.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Upload directory not found. No files have been uploaded yet.",
        )

    # Search for any file starting with the file_id
    matches = list(upload_dir.glob(f"{file_id}.*"))
    if not matches:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No uploaded file found for file_id: {file_id}",
        )

    return matches[0]


@router.post(
    "/{file_id}",
    summary="Parse an uploaded financial file",
    description="Reads a previously uploaded file, detects columns, "
                "normalizes data, and returns structured transactions.",
)
async def parse_file(file_id: str):
    """
    Parse a previously uploaded file into structured transactions.

    Steps:
    1. Locate the file by file_id
    2. Run the parsing engine (column detection + normalization)
    3. Return parsed transactions with metadata, or correction request if needed
    """

    # Find the file
    file_path = _find_uploaded_file(file_id)
    original_filename = file_path.name

    # Parse
    try:
        result = parse_transactions(
            file_path=str(file_path),
            file_id=file_id,
            original_filename=original_filename,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Failed to parse file: {str(e)}",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error during parsing: {str(e)}",
        )

    # Check if correction is needed
    if result.column_mapping.confidence < 0.5:
        # Return correction needed response
        df = read_file_to_dataframe(str(file_path))  # Need to re-read for sample
        sample_data = df.head(5).to_dict('records') if not df.empty else []
        detected_columns = list(df.columns) if not df.empty else []
        
        return CorrectionNeededResponse(
            status="correction_needed",
            message="Column mapping confidence is low. Please confirm column mappings.",
            data={
                "file_id": file_id,
                "original_filename": original_filename,
                "detected_columns": detected_columns,
                "column_mapping": result.column_mapping.model_dump(),
                "sample_data": sample_data,
            }
        )

    return ParseResponse(
        status="success",
        message=f"Parsed {result.summary.valid_rows} valid transactions "
                f"out of {result.summary.total_rows} rows",
        data=result,
    )


@router.post(
    "/{file_id}/correct",
    summary="Parse with corrected column mappings",
    description="Re-parses the file using user-provided column mappings.",
)
async def parse_with_correction(
    file_id: str,
    correction: ColumnCorrectionRequest,
):
    """
    Parse a file with user-corrected column mappings.

    Steps:
    1. Locate the file by file_id
    2. Use provided mappings to override detection
    3. Run parsing with corrected mappings
    4. Run full analysis pipeline
    5. Return results
    """

    # Find the file
    file_path = _find_uploaded_file(file_id)
    original_filename = file_path.name

    # Parse with correction
    try:
        column_mapping = ColumnMapping(
            **correction.model_dump(),
            confidence=1.0,
        )
        result = parse_transactions_with_mapping(
            file_path=str(file_path),
            file_id=file_id,
            original_filename=original_filename,
            column_mapping=column_mapping,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Failed to parse file: {str(e)}",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error during parsing: {str(e)}",
        )

    # Run full pipeline like upload
    from app.services.categorizer import categorize_transactions
    from app.services.analyzer import run_analysis
    from app.services.profiler import generate_profile
    from app.services.analysis_session_service import persist_analysis_session
    from app.services.store import FileResults, save_results

    results = FileResults(file_id=file_id, original_filename=original_filename)
    results.parse_result = result

    try:
        # 2. Categorize
        results.categorization_result = categorize_transactions(results.parse_result)

        # 3. Analyze
        results.analysis_result = run_analysis(
            file_id=file_id,
            transactions=results.categorization_result.transactions,
        )

        # 4. Profile
        results.profile_result = generate_profile(
            file_id=file_id,
            analysis=results.analysis_result,
        )

        # Persist session
        session_id = await persist_analysis_session(results)
        save_results(file_id, results)

        return {
            "status": "success",
            "message": "Analysis complete with corrected mappings",
            "data": {
                "file_id": file_id,
                "session_id": session_id,
            }
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Pipeline failed: {str(e)}",
        )
