import threading
import logging
import uuid
from typing import Optional
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models.ingestion import IngestionJob
from app.ingestion.service import execute_pipeline, cleanup_job_outputs, restore_source_for_job

logger = logging.getLogger(__name__)

def dispatch_pipeline(job_id: uuid.UUID, file_path: str):
    """
    Dispatches the execute_pipeline function to a background thread.
    Uses its own database session.
    """
    def _run_pipeline():
        db: Session = SessionLocal()
        try:
            job = db.query(IngestionJob).filter(IngestionJob.id == job_id).first()
            if not job:
                logger.error(f"[Worker] Ingestion job {job_id} not found in background thread.")
                return
            
            logger.info(f"[Worker] Starting pipeline for job {job_id} in background.")
            execute_pipeline(db, job, file_path)
        except Exception as e:
            logger.exception(f"[Worker] Unhandled exception in pipeline thread for job {job_id}: {e}")
        finally:
            db.close()

    thread = threading.Thread(target=_run_pipeline, daemon=True)
    thread.start()

def dispatch_retry(job_id: uuid.UUID):
    """
    Dispatches the retry execution logic to a background thread.
    Uses its own database session.
    """
    def _run_retry():
        db: Session = SessionLocal()
        try:
            job = db.query(IngestionJob).filter(IngestionJob.id == job_id).first()
            if not job:
                logger.error(f"[Worker] Ingestion job {job_id} not found in background thread.")
                return

            logger.info(f"[Worker] Starting retry for job {job_id} in background.")
            
            # Step 2: Verify & restore durable source BEFORE cleanup
            try:
                file_path = restore_source_for_job(db, job)
            except Exception as e:
                # Error classification already handled in restore_source_for_job
                # and in service.retry_ingestion_job for synchronous path
                logger.error(f"[Worker] Source restoration failed for retry {job_id}: {e}")
                return

            # Step 3: ONLY NOW perform idempotent output cleanup
            cleanup_job_outputs(db, job.id)

            # Step 4: Re-execute pipeline on verified source
            execute_pipeline(db, job, file_path)
            
        except Exception as e:
            logger.exception(f"[Worker] Unhandled exception in retry thread for job {job_id}: {e}")
        finally:
            db.close()

    thread = threading.Thread(target=_run_retry, daemon=True)
    thread.start()

def recover_stale_jobs():
    """
    Called on app startup to find any jobs that were left in a non-terminal state
    (e.g., due to a server crash) and re-dispatch them as retries.
    """
    db: Session = SessionLocal()
    try:
        active_states = [
            "QUEUED", "PROCESSING", "PARSING", "ENTITY_EXTRACTION", 
            "ENTITY_RESOLUTION", "RELATIONSHIP_EXTRACTION", "DOCUMENT_CHUNKING", 
            "EMBEDDING_GENERATION", "VECTOR_PERSISTENCE", "EVIDENCE_LINKING", "NEO4J_SYNC"
        ]
        
        stale_jobs = db.query(IngestionJob).filter(IngestionJob.status.in_(active_states)).all()
        
        for job in stale_jobs:
            logger.info(f"[Worker] Recovering stale job {job.id} (was in state {job.status})")
            
            # Reset state for retry
            job.status = "PROCESSING"
            job.retry_count = (job.retry_count or 0) + 1
            job.recovery_status = "NONE"
            db.commit()
            
            dispatch_retry(job.id)
            
    except Exception as e:
        logger.exception(f"[Worker] Error recovering stale jobs: {e}")
    finally:
        db.close()
