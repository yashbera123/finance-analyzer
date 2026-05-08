"""
Analyze Endpoint
================
POST /analyze/{file_id} — runs the full behavioral analysis pipeline:
  upload → parse → categorize → analyze → profile → persist session

Returns only `session_id` for GET /session/{session_id}.
"""

from pathlib import Path

from fastapi import APIRouter, HTTPException, status

from app.schemas.session import AnalyzeSessionResponse
from app.services.analyzer import run_analysis
from app.services.analysis_session_service import persist_analysis_session
from app.services.categorizer import categorize_transactions
from app.services.parser import parse_transactions, validate_parse_result
from app.services.profiler import generate_profile
from app.services.store import FileResults, save_results
from app.utils.file_helpers import UPLOAD_DIR

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
    response_model=AnalyzeSessionResponse,
    summary="Run behavioral analysis on an uploaded file",
    description="Full pipeline: parse → categorize → analyze → profile → persist session.",
)
async def analyze_file(file_id: str):
    """
    Run the complete behavioral analysis pipeline and persist results.

    Returns only the session id for subsequent GET /session/{session_id} calls.
    """
    file_path = _find_uploaded_file(file_id)

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

    cat_result = categorize_transactions(parse_result)

    try:
        analysis = run_analysis(
            file_id=file_id,
            transactions=cat_result.transactions,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Analysis failed: {str(e)}",
        )

    try:
        profile_result = generate_profile(file_id=file_id, analysis=analysis)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Profile generation failed: {str(e)}",
        )

    results = FileResults(
        file_id=file_id,
        original_filename=file_path.name,
        parse_result=parse_result,
        categorization_result=cat_result,
        analysis_result=analysis,
        profile_result=profile_result,
    )
    save_results(file_id, results)

    session_id = await persist_analysis_session(results)

    return AnalyzeSessionResponse(session_id=session_id)
