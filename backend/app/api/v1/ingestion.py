"""
Ingestion API endpoints.

POST /ingestion/upload    — Upload a file for ingestion
GET  /ingestion/          — List ingestion jobs
GET  /ingestion/{job_id}  — Get job details
GET  /ingestion/{job_id}/entities — Get extracted entity candidates
"""
import os
import uuid
import logging
from typing import List

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_active_user, RoleChecker
from app.models.user import User
from app.models.ingestion import IngestionJob, EntityCandidate
from app.ingestion.schemas import (
    IngestionJobResponse,
    IngestionJobDetailResponse,
    EntityCandidateResponse,
    SourceType,
)
from app.ingestion.service import validate_file, process_ingestion, UPLOAD_DIR
from app.ingestion.worker import dispatch_pipeline, dispatch_retry

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/upload", response_model=IngestionJobResponse, status_code=status.HTTP_202_ACCEPTED)
async def upload_file(
    file: UploadFile = File(...),
    source_type: str = Form(default="OTHER"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    _ = Depends(RoleChecker(["OFFICER", "ADMIN", "SUPER_ADMIN"]))
):
    """
    Upload a file for ingestion and NLP extraction.

    Supported formats: PDF, CSV, JSON, TXT.
    The file is validated and saved synchronously. The pipeline is dispatched
    to a background thread, and the job is returned immediately in QUEUED state.
    """
    # ── Validate ────────────────────────────────────────────────────────
    try:
        # Read file content
        content = await file.read()
        file_size = len(content)

        file_ext = validate_file(
            filename=file.filename or "",
            content_type=file.content_type,
            file_size=file_size,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e),
        )

    # Validate source_type
    try:
        validated_source = SourceType(source_type)
    except ValueError:
        # Accept it as-is if it doesn't match the enum (for flexibility)
        validated_source = SourceType.OTHER

    # ── Save file ───────────────────────────────────────────────────────
    safe_filename = f"{uuid.uuid4().hex}_{file.filename}"
    file_path = str(UPLOAD_DIR / safe_filename)

    try:
        with open(file_path, "wb") as f:
            f.write(content)
    except Exception as e:
        logger.error(f"Failed to save uploaded file: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to save uploaded file.",
        )

    # ── Process ─────────────────────────────────────────────────────────
    try:
        # Create the job and store source durably (synchronous)
        job = process_ingestion(
            db=db,
            file_path=file_path,
            file_name=file.filename or "unknown",
            file_type=file_ext,
            source_type=validated_source.value,
            file_size=file_size,
            user_id=current_user.id,
            file_bytes=content,
            content_type=file.content_type or "application/octet-stream",
            execute_sync=False  # Tell service NOT to run execute_pipeline
        )
        
        # Dispatch the heavy pipeline to the background
        dispatch_pipeline(job.id, file_path)
        
    except Exception as e:
        logger.error(f"Ingestion processing error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred during file processing.",
        )

    return job


@router.get("/", response_model=List[IngestionJobResponse])
def list_ingestion_jobs(
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """List all ingestion jobs, most recent first."""
    jobs = (
        db.query(IngestionJob)
        .filter(IngestionJob.is_deleted == False)
        .order_by(IngestionJob.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    return jobs


@router.get("/{job_id}", response_model=IngestionJobDetailResponse)
def get_ingestion_job(
    job_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get detailed information about an ingestion job, including extracted entities."""
    job = (
        db.query(IngestionJob)
        .filter(IngestionJob.id == job_id, IngestionJob.is_deleted == False)
        .first()
    )
    if not job:
        raise HTTPException(status_code=404, detail="Ingestion job not found.")

    entities = (
        db.query(EntityCandidate)
        .filter(EntityCandidate.ingestion_job_id == job_id)
        .order_by(EntityCandidate.entity_type, EntityCandidate.created_at)
        .all()
    )

    # Build the detail response
    response = IngestionJobDetailResponse.model_validate(job)
    response.entities = [EntityCandidateResponse.model_validate(e) for e in entities]
    return response


@router.get("/{job_id}/entities", response_model=List[EntityCandidateResponse])
def get_job_entities(
    job_id: uuid.UUID,
    entity_type: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get extracted entity candidates for an ingestion job, optionally filtered by type."""
    # Verify the job exists
    job = (
        db.query(IngestionJob)
        .filter(IngestionJob.id == job_id, IngestionJob.is_deleted == False)
        .first()
    )
    if not job:
        raise HTTPException(status_code=404, detail="Ingestion job not found.")

    query = db.query(EntityCandidate).filter(EntityCandidate.ingestion_job_id == job_id)

    if entity_type:
        query = query.filter(EntityCandidate.entity_type == entity_type.upper())

    entities = query.order_by(EntityCandidate.entity_type, EntityCandidate.created_at).all()
    return entities


@router.post("/{job_id}/retry", response_model=IngestionJobResponse, status_code=status.HTTP_202_ACCEPTED)
def retry_job(
    job_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    _ = Depends(RoleChecker(["OFFICER", "ADMIN", "SUPER_ADMIN"]))
):
    """
    Retry an ingestion job that failed or partially completed.
    Requires OFFICER, ADMIN, or SUPER_ADMIN authorization.
    Prevents simultaneous duplicate retries using atomic database status checks.
    The retry is dispatched to a background thread.
    """
    job = db.query(IngestionJob).filter(IngestionJob.id == job_id, IngestionJob.is_deleted == False).first()
    if not job:
        raise HTTPException(status_code=404, detail="Ingestion job not found.")

    if job.status not in ("FAILED", "COMPLETED_PARTIAL"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Job status '{job.status}' is not eligible for retry."
        )

    if (job.retry_count or 0) >= (job.max_retry_count or 3) and job.recovery_status in ("EXHAUSTED", "PERMANENT_FAILURE"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Maximum retries ({job.max_retry_count}) reached for job {job_id}."
        )

    # Atomic Concurrency Lock: Transition status to PROCESSING atomically if in FAILED/COMPLETED_PARTIAL
    affected_rows = db.query(IngestionJob).filter(
        IngestionJob.id == job_id,
        IngestionJob.status.in_(["FAILED", "COMPLETED_PARTIAL"])
    ).update({"status": "PROCESSING"}, synchronize_session=False)
    db.commit()

    if affected_rows == 0:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Job is currently being retried or processed by another request."
        )

    try:
        dispatch_retry(job_id)
        
        # Fetch fresh job to return
        updated_job = db.query(IngestionJob).filter(IngestionJob.id == job_id).first()
        return updated_job
    except Exception as e:
        logger.error(f"Retry dispatch error for job {job_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to dispatch retry for ingestion job: {e}"
        )

