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

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/upload", response_model=IngestionJobResponse, status_code=status.HTTP_201_CREATED)
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
    The file is validated, parsed, and entities are extracted synchronously.
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
        job = process_ingestion(
            db=db,
            file_path=file_path,
            file_name=file.filename or "unknown",
            file_type=file_ext,
            source_type=validated_source.value,
            file_size=file_size,
            user_id=current_user.id,
        )
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
