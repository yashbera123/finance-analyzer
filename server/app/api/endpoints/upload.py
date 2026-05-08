"""
Upload Endpoint
===============
POST /upload — accepts CSV and Excel files, validates, stores temporarily,
runs the full analysis pipeline, and returns results summary.
"""

from datetime import datetime, timezone
import logging

from fastapi import APIRouter, HTTPException, UploadFile, File, status

from app.schemas.upload import FileMetadata, UploadResponse
from app.schemas.transaction import CorrectionNeededResponse
from app.services.categorizer import categorize_transactions
from app.services.analyzer import run_analysis
from app.services.parser import parse_transactions, validate_parse_result, read_file_to_dataframe
from app.services.profiler import generate_profile
from app.services.analysis_session_service import persist_analysis_session
from app.services.store import FileResults, save_results
from app.utils.file_helpers import (
    MAX_FILE_SIZE_BYTES,
    MAX_FILE_SIZE_MB,
    generate_file_id,
    get_file_type_label,
    humanize_bytes,
    save_temp_file,
    validate_content_type,
    validate_file_extension,
)

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post(
    "/",
    summary="Upload and analyze a financial data file",
    description="Accepts financial data files "
                "(.csv/.tsv/.txt/.xlsx/.xlsm/.xls/.pdf/.docx/.doc) up to 10 MB. "
                "Automatically runs parse → categorize → analyze → profile. "
                "Returns file metadata; results available via GET endpoints.",
)
async def upload_file(
    file: UploadFile = File(
        ...,
        description="Delimited text or spreadsheet file",
    ),
):
    """
    Upload a financial data file and run the full analysis pipeline.

    Steps:
    1. Validate and store the file
    2. Parse transactions
    3. Categorize each transaction
    4. Run behavioral analysis
    5. Generate financial profile
    6. Cache all results for retrieval
    """

    # --- Validate filename exists -------------------------------------------
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Filename is missing from the upload.",
        )

    # --- Validate extension -------------------------------------------------
    if not validate_file_extension(file.filename):
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="Unsupported file type. Allowed: .csv, .tsv, .txt, .xlsx, .xlsm, .xls, .pdf, .docx, .doc",
        )

    # --- Validate content type ----------------------------------------------
    if file.content_type and not validate_content_type(file.content_type, file.filename):
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=f"Unsupported content type: {file.content_type}",
        )

    # --- Read file contents -------------------------------------------------
    contents = await file.read()

    # --- Validate size ------------------------------------------------------
    if len(contents) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file is empty.",
        )

    if len(contents) > MAX_FILE_SIZE_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File exceeds maximum size of {MAX_FILE_SIZE_MB} MB.",
        )

    # --- Store temporarily --------------------------------------------------
    file_id = generate_file_id()
    stored_path = await save_temp_file(file_id, file.filename, contents)
    logger.info(
        "Upload received file_id=%s filename=%s size_bytes=%d stored_path=%s",
        file_id,
        file.filename,
        len(contents),
        stored_path,
    )

    # --- Run full pipeline --------------------------------------------------
    results = FileResults(file_id=file_id, original_filename=file.filename)

    try:
        # 1. Parse
        results.parse_result = parse_transactions(
            file_path=stored_path,
            file_id=file_id,
            original_filename=file.filename,
        )

        # Check if correction is needed
        if results.parse_result.column_mapping.confidence < 0.5:
            # Return correction needed
            df = read_file_to_dataframe(stored_path)
            sample_data = df.head(5).to_dict('records') if not df.empty else []
            detected_columns = list(df.columns) if not df.empty else []
            
            return CorrectionNeededResponse(
                status="correction_needed",
                message="Column mapping confidence is low. Please confirm column mappings.",
                data={
                    "file_id": file_id,
                    "original_filename": file.filename,
                    "detected_columns": detected_columns,
                    "column_mapping": results.parse_result.column_mapping.model_dump(),
                    "sample_data": sample_data,
                }
            )

        validate_parse_result(results.parse_result)

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
        logger.info(
            "Upload pipeline complete file_id=%s parsed=%d categorized=%d income=%s spending=%s",
            file_id,
            results.parse_result.summary.valid_rows,
            len(results.categorization_result.transactions),
            results.analysis_result.savings.total_income,
            results.analysis_result.savings.total_spending,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Pipeline failed: {str(e)}",
        )

    # --- Cache results ------------------------------------------------------
    save_results(file_id, results)

    # --- Persist session (survives navigation / new requests) ---------------
    session_id = await persist_analysis_session(results)

    # --- Build response -----------------------------------------------------
    txn_count = len(results.parse_result.transactions) if results.parse_result else 0
    cat_count = (
        results.categorization_result.summary.categorized_count
        if results.categorization_result else 0
    )

    metadata = FileMetadata(
        file_id=file_id,
        session_id=session_id,
        original_filename=file.filename,
        file_type=get_file_type_label(file.filename),
        file_size_bytes=len(contents),
        file_size_human=humanize_bytes(len(contents)),
        stored_path=stored_path,
        uploaded_at=datetime.now(timezone.utc),
    )

    return UploadResponse(
        status="success",
        message=(
            f"File processed: {txn_count} transactions parsed, "
            f"{cat_count} categorized"
        ),
        data=metadata,
    )
