"""
Ingestion service: orchestrates the full pipeline.

File Upload → Validation → Parsing → NLP Extraction → Persistence
→ RAG Vector Indexing (Step 6)

This service is synchronous. For M1.3, this is appropriate since
we are not introducing Celery/Redis complexity yet.
"""
import os
import logging
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional


from sqlalchemy.orm import Session

from app.models.ingestion import IngestionJob, EntityCandidate
from app.ingestion.parsers import ParsedDocument
from app.ingestion.parsers.pdf_parser import parse_pdf
from app.ingestion.parsers.txt_parser import parse_txt
from app.ingestion.parsers.csv_parser import parse_csv
from app.ingestion.parsers.json_parser import parse_json
from app.nlp.extractor import extract_entities
from app.nlp.llm_extractor import extract_entities_llm
from app.nlp.resolution.engine import resolve_candidate
from app.nlp.resolution.normalization import normalize_entity
from app.nlp.resolution.schemas import ResolutionContext
from app.ai.rag.vector_search import VectorStore
from app.ingestion.storage import (
    get_storage_provider,
    make_storage_key,
    calculate_sha256,
    StorageKeyNotFoundError,
    StorageUnavailableError,
    StoragePermissionError,
    StorageUploadError,
)
from langchain_text_splitters import RecursiveCharacterTextSplitter

logger = logging.getLogger(__name__)

# ── Configuration ───────────────────────────────────────────────────────

UPLOAD_DIR = Path(__file__).resolve().parent.parent.parent / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

ALLOWED_EXTENSIONS = {"pdf", "csv", "json", "txt"}
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50 MB

MIME_TYPE_MAP = {
    "application/pdf": "pdf",
    "text/csv": "csv",
    "application/json": "json",
    "text/plain": "txt",
    "text/json": "json",
    "application/octet-stream": None,  # Will rely on extension
}

PARSER_MAP = {
    "pdf": parse_pdf,
    "csv": parse_csv,
    "json": parse_json,
    "txt": parse_txt,
}


# ── Validation ──────────────────────────────────────────────────────────

def validate_file(filename: str, content_type: Optional[str], file_size: int) -> str:
    """
    Validate an uploaded file. Returns the normalized file extension.

    Raises:
        ValueError: If the file is invalid.
    """
    if not filename or not filename.strip():
        raise ValueError("Filename is required.")

    # Extract extension
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    if ext not in ALLOWED_EXTENSIONS:
        raise ValueError(
            f"Unsupported file type '.{ext}'. "
            f"CSV, JSON, PDF, and TXT files are supported."
        )

    # Check MIME type if available
    if content_type:
        mapped_ext = MIME_TYPE_MAP.get(content_type)
        if mapped_ext is not None and mapped_ext != ext:
            logger.warning(
                f"MIME type '{content_type}' does not match extension '.{ext}'. "
                f"Proceeding with extension-based detection."
            )

    # Check file size
    if file_size <= 0:
        raise ValueError("Uploaded file is empty.")
    if file_size > MAX_FILE_SIZE:
        raise ValueError(f"File exceeds maximum size of {MAX_FILE_SIZE // (1024*1024)} MB.")

    return ext


# ── Pipeline ────────────────────────────────────────────────────────────

# ── RAG Chunking Configuration ──────────────────────────────────────────
# Matches the parameters established in scripts/ingest_fir_pdfs.py.
# chunk_size is in characters (not tokens). At ~4 chars/token this is
# roughly 250 tokens — well within all-MiniLM-L6-v2's 256-token window.
# Lazy-initialized so that langchain_text_splitters (and its transitive
# dependency on torch/sentence_transformers) is only imported the first
# time RAG chunking is actually needed, not at module import time.
_CHUNK_SPLITTER = None


def _get_chunk_splitter():
    global _CHUNK_SPLITTER
    if _CHUNK_SPLITTER is None:
        from langchain_text_splitters import RecursiveCharacterTextSplitter
        _CHUNK_SPLITTER = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
            is_separator_regex=False,
        )
    return _CHUNK_SPLITTER


import re

# ── Reliability & Error Classification Helpers (M15.7) ───────────────────

def sanitize_error_message(msg: str) -> str:
    """Sanitize secrets, JWTs, credentials, and tokens from error messages."""
    if not msg:
        return ""
    msg = re.sub(r'bearer\s+[a-zA-Z0-9\-\._~\+\/]+=*', 'Bearer [REDACTED]', msg, flags=re.IGNORECASE)
    msg = re.sub(r'key=[a-zA-Z0-9\-_]+', 'key=[REDACTED]', msg, flags=re.IGNORECASE)
    msg = re.sub(r'password=[^\s&]+', 'password=[REDACTED]', msg, flags=re.IGNORECASE)
    msg = re.sub(r'postgres://[^\s]+', 'postgres://[REDACTED]', msg, flags=re.IGNORECASE)
    return msg[:2000]


def classify_error(exc: Exception, current_step: str) -> tuple[str, str, str]:
    """
    Classifies exception into (error_code, recovery_status, sanitized_message).
    recovery_status: 'RETRYABLE' or 'PERMANENT_FAILURE'

    M15.7.1 note: SOURCE_FILE_MISSING is classified as RETRYABLE when
    the caller knows a durable copy exists. The distinction is:
        - StorageKeyNotFoundError  → SOURCE_FILE_MISSING PERMANENT_FAILURE
          (durable copy does not exist, cannot recover)
        - StorageUnavailableError  → SOURCE_STORAGE_UNAVAILABLE RETRYABLE
          (backend temporarily down, can retry later)
        - FileNotFoundError (local only, durable exists) → RETRYABLE
          (resolved by restore_source_for_job before this function is called)
    """
    err_str = str(exc)
    sanitized = sanitize_error_message(err_str)

    # M15.7.1 — Storage-specific classification
    if isinstance(exc, StorageKeyNotFoundError):
        return "SOURCE_FILE_MISSING", "PERMANENT_FAILURE", sanitized
    if isinstance(exc, StorageUnavailableError):
        return "SOURCE_STORAGE_UNAVAILABLE", "RETRYABLE", sanitized
    if isinstance(exc, StoragePermissionError):
        return "SOURCE_STORAGE_PERMISSION_ERROR", "PERMANENT_FAILURE", "Storage authentication failed. Check SUPABASE_SERVICE_ROLE_KEY or provider configuration."

    if isinstance(exc, (ValueError, TypeError, FileNotFoundError)):
        if "contains no extractable text" in err_str or "Unsupported file type" in err_str or "No parser available" in err_str:
            return "UNSUPPORTED_OR_CORRUPT_DOCUMENT", "PERMANENT_FAILURE", sanitized
        if isinstance(exc, FileNotFoundError):
            # FileNotFoundError here = local file missing AND no durable source
            # (if durable source existed, restore_source_for_job would have recovered it)
            return "SOURCE_FILE_MISSING", "PERMANENT_FAILURE", sanitized

    if current_step == "PARSING":
        is_perm = any(k in err_str.lower() for k in ("corrupt", "unsupported", "invalid pdf", "no text"))
        return "PARSER_FAILURE", "PERMANENT_FAILURE" if is_perm else "RETRYABLE", sanitized
    elif current_step in ("EMBEDDING_GENERATION", "VECTOR_PERSISTENCE"):
        return "EMBEDDING_PROVIDER_UNAVAILABLE", "RETRYABLE", sanitized
    elif current_step == "NEO4J_SYNC":
        return "NEO4J_UNAVAILABLE", "RETRYABLE", sanitized

    if any(k in err_str.lower() for k in ("connection", "timeout", "refused", "unavailable", "network")):
        return "SERVICE_UNAVAILABLE", "RETRYABLE", sanitized

    return "UNEXPECTED_ERROR", "RETRYABLE", sanitized


def cleanup_job_outputs(db: Session, job_id: uuid.UUID) -> None:
    """
    Safely purges any partial/previous outputs produced by an ingestion job
    (EntityCandidate, EntityRelationship, EvidenceLink, DocumentChunk).
    Ensures retry operations perform clean idempotent writes.
    """
    from app.models.relationship import EntityRelationship
    from app.models.evidence_link import EvidenceLink
    from app.models.document import DocumentChunk

    rel_ids = [r.id for r in db.query(EntityRelationship.id).filter(EntityRelationship.ingestion_job_id == job_id).all()]
    cand_ids = [c.id for c in db.query(EntityCandidate.id).filter(EntityCandidate.ingestion_job_id == job_id).all()]
    chunk_ids = [chk.id for chk in db.query(DocumentChunk.id).filter(DocumentChunk.ingestion_job_id == job_id).all()]

    if rel_ids or cand_ids or chunk_ids:
        db.query(EvidenceLink).filter(
            (EvidenceLink.relationship_id.in_(rel_ids)) |
            (EvidenceLink.candidate_id.in_(cand_ids)) |
            (EvidenceLink.document_chunk_id.in_(chunk_ids))
        ).delete(synchronize_session=False)

    db.query(EntityRelationship).filter(EntityRelationship.ingestion_job_id == job_id).delete(synchronize_session=False)
    db.query(EntityCandidate).filter(EntityCandidate.ingestion_job_id == job_id).delete(synchronize_session=False)
    db.query(DocumentChunk).filter(DocumentChunk.ingestion_job_id == job_id).delete(synchronize_session=False)

    db.commit()
    logger.info(f"Cleaned up previous outputs for ingestion job {job_id}")


def execute_pipeline(
    db: Session,
    job: IngestionJob,
    file_path: str,
) -> IngestionJob:
    """
    Runs the ingestion pipeline steps on an established IngestionJob record.
    Tracks step execution and failure metadata for observability & recovery.
    """
    current_step = "PARSING"
    file_type = job.file_type
    source_type = job.source_type
    file_name = job.file_name

    try:
        # ── Step 2: Parse ───────────────────────────────────────────────
        current_step = "PARSING"
        job.status = "PARSING"
        job.current_step = current_step
        job.started_at = datetime.now(timezone.utc)
        db.commit()

        parser = PARSER_MAP.get(file_type)
        if parser is None:
            raise ValueError(f"No parser available for file type: {file_type}")

        parsed: ParsedDocument = parser(file_path)

        job.status = "PARSED"
        job.record_count = parsed.record_count
        job.progress_detail = {"parsed_records": parsed.record_count}
        db.commit()

        # ── Step 3: NLP Extraction ──────────────────────────────────────
        current_step = "ENTITY_EXTRACTION"
        job.status = current_step
        job.current_step = current_step
        db.commit()
        all_candidates: list[EntityCandidate] = []

        for page in parsed.pages:
            if not page.text.strip():
                continue

            page_offset = parsed.raw_text.find(page.text) if len(parsed.pages) > 1 else 0
            extracted = extract_entities(page.text, page_offset=max(0, page_offset))

            for ent in extracted:
                candidate = EntityCandidate(
                    ingestion_job_id=job.id,
                    entity_type=ent.entity_type,
                    raw_text=ent.raw_text,
                    normalized_value=ent.normalized_value,
                    confidence=ent.confidence,
                    source_page=page.page_number if file_type in ("pdf", "txt") else None,
                    source_row=page.page_number if file_type in ("csv", "json") else None,
                    start_offset=ent.start_offset,
                    end_offset=ent.end_offset,
                    extraction_method=ent.extraction_method,
                )
                all_candidates.append(candidate)

            if file_type in ("csv", "json") and "fields" in page.metadata:
                structured = _extract_structured_fields(
                    page.metadata["fields"],
                    job_id=job.id,
                    row_number=page.page_number,
                )
                all_candidates.extend(structured)

        # ── Step 3b: LLM Semantic Extraction (FIRs only) ────────────────
        if source_type in ("FIR", "POLICE_REPORT"):
            for page in parsed.pages:
                if not page.text.strip():
                    continue

                page_offset = parsed.raw_text.find(page.text) if len(parsed.pages) > 1 else 0
                llm_extracted = extract_entities_llm(
                    text=page.text,
                    source_page=page.page_number if file_type == "pdf" else None,
                    source_row=page.page_number if file_type in ("csv", "json") else None,
                    page_offset=max(0, page_offset)
                )

                for ent in llm_extracted:
                    is_duplicate = any(
                        c.normalized_value == ent.normalized_value and c.entity_type == ent.entity_type
                        for c in all_candidates
                    )
                    if not is_duplicate:
                        candidate = EntityCandidate(
                            ingestion_job_id=job.id,
                            entity_type=ent.entity_type,
                            raw_text=ent.raw_text,
                            normalized_value=ent.normalized_value,
                            confidence=ent.confidence,
                            source_page=page.page_number if file_type in ("pdf", "txt") else None,
                            source_row=page.page_number if file_type in ("csv", "json") else None,
                            extraction_method=ent.extraction_method,
                        )
                        all_candidates.append(candidate)

        job.status = "EXTRACTED"
        job.entity_count = len(all_candidates)
        job.progress_detail = {**job.progress_detail, "extracted_entities": len(all_candidates)} if job.progress_detail else {"extracted_entities": len(all_candidates)}
        db.commit()

        # ── Step 4: Persist candidates & Resolution ──────────────────────
        current_step = "ENTITY_RESOLUTION"
        job.status = current_step
        job.current_step = current_step
        db.commit()
        if all_candidates:
            for candidate in all_candidates:
                context = ResolutionContext()

                if candidate.entity_type in ("PERSON", "ORGANIZATION", "LOCATION"):
                    same_scope = [
                        c for c in all_candidates 
                        if c != candidate and (
                            (candidate.source_page and c.source_page == candidate.source_page) or
                            (candidate.source_row and c.source_row == candidate.source_row)
                        )
                    ]
                    for c in same_scope:
                        if c.entity_type == "PHONE" and c.normalized_value:
                            context.phones.append(c.normalized_value)
                        elif c.entity_type == "VEHICLE" and c.normalized_value:
                            context.vehicles.append(c.normalized_value)
                        elif c.entity_type == "LOCATION" and c.normalized_value:
                            context.locations.append(c.normalized_value)
                        elif c.entity_type == "ORGANIZATION" and c.normalized_value:
                            context.organizations.append(c.normalized_value)
                        elif c.entity_type == "DATE" and c.normalized_value:
                            context.dates.append(c.normalized_value)

                status, canonical_id, score, evidence = resolve_candidate(db, candidate, context)
                candidate.resolution_status = status
                candidate.resolved_to_id = canonical_id
                candidate.resolution_score = score
                candidate.resolution_evidence = evidence

            db.add_all(all_candidates)
            db.commit()

            # ── Step 5: Relationship Extraction ─────────────────────────────
            current_step = "RELATIONSHIP_EXTRACTION"
            job.status = current_step
            job.current_step = current_step
            db.commit()
            from app.nlp.relationship import extract_relationships_for_page
            total_rels = 0
            for page in parsed.pages:
                page_candidates = [
                    c for c in all_candidates 
                    if c.source_page == page.page_number or c.source_row == page.page_number
                ]
                rels = extract_relationships_for_page(db, job, page, page_candidates)
                if rels:
                   total_rels += len(rels)
            job.relationship_count = total_rels
            job.progress_detail = {**job.progress_detail, "extracted_relationships": total_rels} if job.progress_detail else {"extracted_relationships": total_rels}
            db.commit()

        job.entity_count = len(all_candidates)

        # ── Step 6: RAG Vector Indexing ──────────────────────────────────
        current_step = "EMBEDDING_GENERATION"
        job.status = current_step
        job.current_step = current_step
        db.commit()
        chunk_count = 0
        attempted_chunks = 0
        try:
            vs = VectorStore()
            doc_total_pages = parsed.record_count

            for page in parsed.pages:
                if not page.text.strip():
                    continue

                raw_chunks = _get_chunk_splitter().split_text(page.text)
                total_chunks_on_page = len(raw_chunks)

                for chunk_index, chunk_text in enumerate(raw_chunks):
                    if not chunk_text.strip():
                        continue

                    attempted_chunks += 1
                    metadata: dict = {
                        "ingestion_job_id": str(job.id),
                        "source_filename": file_name,
                        "source_type": source_type,
                        "file_type": file_type,
                        "page_number": page.page_number,
                        "chunk_index": chunk_index,
                        "total_chunks_on_page": total_chunks_on_page,
                        "total_pages": doc_total_pages,
                    }

                    for k, v in page.metadata.items():
                        if isinstance(v, (str, int, float, bool)) and k not in metadata:
                            metadata[k] = v

                    success = vs.index_document(
                        ingestion_job_id=job.id,
                        text=chunk_text,
                        chunk_index=chunk_index,
                        page_number=page.page_number if file_type in ("pdf", "txt") else None,
                        source_row=page.page_number if file_type in ("csv", "json") else None,
                        metadata=metadata,
                        db=db,
                    )

                    if success:
                        chunk_count += 1

            # ── Step 7: Phase 2 Evidence Linking ─────────────────────────────
            current_step = "EVIDENCE_LINKING"
            job.status = current_step
            job.current_step = current_step
            db.commit()
            if chunk_count > 0:
                try:
                    from app.ingestion.evidence_linker import link_evidence_for_job
                    link_evidence_for_job(db, job)
                except Exception as link_err:
                    logger.warning(f"Ingestion job {job.id}: Evidence linking warning: {link_err}")

            # ── Step 8: Neo4j Synchronization ────────────────────────────────
            current_step = "NEO4J_SYNC"
            job.status = current_step
            job.current_step = current_step
            db.commit()
            
            try:
                from app.ai.neo4j.intelligence import neo4j_intelligence
                # Sync relationships (and their connected entities)
                from app.models.relationship import EntityRelationship
                rels = db.query(EntityRelationship).filter(EntityRelationship.ingestion_job_id == job.id).all()
                for rel in rels:
                    neo4j_intelligence.sync_relationship(db, rel)
                # Note: standalone entities that aren't in relationships might not get synced here,
                # but that matches current behavior where Neo4j is primarily for the relationship graph.
            except Exception as sync_err:
                logger.warning(f"Ingestion job {job.id}: Neo4j sync warning: {sync_err}")

            if attempted_chunks == 0 or chunk_count == attempted_chunks:
                final_status = "COMPLETED"
                job.error_message = None
            elif chunk_count > 0:
                final_status = "COMPLETED_PARTIAL"
                failed_chunks = attempted_chunks - chunk_count
                job.error_message = (
                    f"Partial RAG indexing: {chunk_count}/{attempted_chunks} chunks indexed; "
                    f"{failed_chunks} chunk(s) failed."
                )
            else:
                final_status = "FAILED"
                job.failed_step = "EMBEDDING_GENERATION"
                job.error_code = "EMBEDDING_PROVIDER_UNAVAILABLE"
                job.error_message = f"Vector indexing failed: 0/{attempted_chunks} chunks indexed into pgvector."
                job.recovery_status = "RETRYABLE"
                job.failed_at = datetime.now(timezone.utc)

        except Exception as vec_err:
            sanitized_vec_msg = sanitize_error_message(str(vec_err))
            logger.warning(f"Ingestion job {job.id}: Vector indexing exception: {sanitized_vec_msg}")
            final_status = "FAILED"
            job.failed_step = "EMBEDDING_GENERATION"
            job.error_code = "EMBEDDING_PROVIDER_UNAVAILABLE"
            job.error_message = f"Vector indexing failed: {sanitized_vec_msg}"
            job.recovery_status = "RETRYABLE"
            job.failed_at = datetime.now(timezone.utc)

        job.chunk_count = chunk_count
        job.progress_detail = {**job.progress_detail, "indexed_chunks": chunk_count} if job.progress_detail else {"indexed_chunks": chunk_count}
        job.status = final_status
        job.current_step = "COMPLETED" if final_status in ("COMPLETED", "COMPLETED_PARTIAL") else "FAILED"
        if final_status in ("COMPLETED", "COMPLETED_PARTIAL"):
            job.failed_step = None
            job.error_code = None
            job.recovery_status = "RECOVERED" if (job.retry_count or 0) > 0 else "NONE"
        job.completed_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(job)

        logger.info(f"Ingestion job {job.id} completed with status {final_status}.")

    except Exception as e:
        err_code, rec_status, sanitized_msg = classify_error(e, current_step)
        logger.error(f"Ingestion job {job.id} failed at step {current_step}: {sanitized_msg}")

        job.status = "FAILED"
        job.failed_step = current_step
        job.error_code = err_code
        job.error_message = sanitized_msg
        job.failed_at = datetime.now(timezone.utc)
        job.completed_at = datetime.now(timezone.utc)

        if (job.retry_count or 0) >= (job.max_retry_count or 3):
            job.recovery_status = "EXHAUSTED"
        else:
            job.recovery_status = rec_status

        db.commit()
        db.refresh(job)

    return job


def _store_source_durably(
    db: Session,
    job: IngestionJob,
    file_bytes: bytes,
    original_filename: str,
    content_type: str,
) -> None:
    """
    Upload the original source bytes to durable storage and record the
    storage reference on the IngestionJob.

    Called during the initial upload (process_ingestion) BEFORE the pipeline
    is executed, so that the durable copy is always available for later retries.

    On storage failure, logs a warning but does NOT raise — the ingestion
    pipeline continues on the local working copy. The job's source_storage_key
    will remain NULL, indicating no durable backup exists.
    """
    try:
        storage = get_storage_provider()
        storage_key = make_storage_key(str(job.id), original_filename)
        sha256 = calculate_sha256(file_bytes)

        storage.upload_source(
            storage_key=storage_key,
            data=file_bytes,
            content_type=content_type or "application/octet-stream",
        )

        # Record durable storage metadata on the job
        job.source_storage_provider = os.environ.get("SOURCE_STORAGE_PROVIDER", "local").lower()
        job.source_storage_key = storage_key
        job.source_original_filename = original_filename
        job.source_content_type = content_type or "application/octet-stream"
        job.source_size_bytes = len(file_bytes)
        job.source_sha256 = sha256
        job.source_storage_bucket = os.environ.get("SOURCE_STORAGE_BUCKET", None)
        job.source_uploaded_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(job)

        logger.info(
            f"[DurableSource] Stored source for job {job.id}: "
            f"provider={job.source_storage_provider} sha256={sha256[:12]}..."
        )

    except Exception as e:
        # Non-fatal: log warning but continue. Retry will detect no durable source.
        logger.warning(
            f"[DurableSource] Could not store source durably for job {job.id}: "
            f"{type(e).__name__} — job will proceed on local copy only."
        )


def restore_source_for_job(
    db: Session,
    job: IngestionJob,
) -> str:
    """
    Locate the source file for an ingestion job, restoring it from durable
    storage if the local working copy is missing.

    Returns the absolute path to the verified local working copy.

    Error Semantics (M15.7.1):
        Local missing + Durable available + SHA-256 matches → restore & return path
        Local missing + Durable available + SHA-256 mismatch → PERMANENT_FAILURE (SOURCE_FILE_INTEGRITY_MISMATCH)
        Local missing + No durable record → PERMANENT_FAILURE (SOURCE_FILE_MISSING)
        Durable missing (key not in storage) → PERMANENT_FAILURE (SOURCE_FILE_MISSING)
        Storage provider temporarily unavailable → RETRYABLE (SOURCE_STORAGE_UNAVAILABLE)

    IMPORTANT: This function must be called BEFORE cleanup_job_outputs() so that
    if restoration fails, the job's existing partial outputs are preserved.
    """
    # ── Step 1: Try to find the existing local working copy ──────────────
    matching_files = list(UPLOAD_DIR.glob(f"*_{job.file_name}"))
    local_path: Optional[str] = None
    if matching_files:
        local_path = str(matching_files[0])
    else:
        candidate = str(UPLOAD_DIR / job.file_name)
        if os.path.exists(candidate):
            local_path = candidate

    if local_path and os.path.exists(local_path):
        # Local file present — verify checksum if we have a durable reference
        if job.source_sha256:
            try:
                existing_bytes = Path(local_path).read_bytes()
                actual_sha256 = calculate_sha256(existing_bytes)
                if actual_sha256 != job.source_sha256:
                    logger.error(
                        f"[DurableSource] INTEGRITY_MISMATCH job={job.id}: "
                        f"local sha256={actual_sha256[:12]} expected={job.source_sha256[:12]}"
                    )
                    _mark_permanent_failure(
                        db, job,
                        error_code="SOURCE_FILE_INTEGRITY_MISMATCH",
                        message="Local source file SHA-256 does not match durable storage checksum. File may be corrupted.",
                    )
                    raise ValueError("Source file integrity mismatch — local file SHA-256 does not match stored checksum.")
            except (OSError, PermissionError) as read_err:
                logger.warning(f"[DurableSource] Cannot read local file for checksum check: {read_err}")
                # Fall through to durable restoration

        logger.debug(f"[DurableSource] Local source found for job {job.id}: {local_path}")
        return local_path

    # ── Step 2: Local file missing — check for durable storage ───────────
    logger.info(f"[DurableSource] Local source not found for job {job.id}, checking durable storage...")

    if not job.source_storage_key:
        # No durable record was ever created — this is a permanent failure
        _mark_permanent_failure(
            db, job,
            error_code="SOURCE_FILE_MISSING",
            message=f"Source file '{job.file_name}' is not available locally and no durable backup was recorded.",
        )
        raise StorageKeyNotFoundError(
            f"Source file '{job.file_name}' is missing and no durable backup exists."
        )

    # ── Step 3: Restore from durable storage ─────────────────────────────
    try:
        storage = get_storage_provider()

        if not storage.source_exists(job.source_storage_key):
            _mark_permanent_failure(
                db, job,
                error_code="SOURCE_FILE_MISSING",
                message=f"Source file not found in durable storage (key: [REDACTED]). Cannot recover.",
            )
            raise StorageKeyNotFoundError(
                f"Source key not found in durable storage for job {job.id}"
            )

        restored_bytes = storage.download_source(job.source_storage_key)

    except (StorageKeyNotFoundError, StoragePermissionError):
        raise  # Already classified as permanent failure above
    except StorageUnavailableError:
        # Transient — do NOT mark permanent failure; allow retry later
        logger.warning(f"[DurableSource] Storage temporarily unavailable for job {job.id}")
        raise
    except Exception as e:
        logger.error(f"[DurableSource] Download failed for job {job.id}: {type(e).__name__}")
        raise StorageUnavailableError(f"Durable storage download failed: {type(e).__name__}") from e

    # ── Step 4: Verify SHA-256 integrity ────────────────────────────────
    if job.source_sha256:
        restored_sha256 = calculate_sha256(restored_bytes)
        if restored_sha256 != job.source_sha256:
            _mark_permanent_failure(
                db, job,
                error_code="SOURCE_FILE_INTEGRITY_MISMATCH",
                message="Restored source file SHA-256 does not match original checksum. Durable copy may be corrupted.",
            )
            raise ValueError(
                f"Restored source for job {job.id} failed SHA-256 verification."
            )
        logger.info(f"[DurableSource] SHA-256 verified OK for job {job.id}: {restored_sha256[:12]}...")

    # ── Step 5: Write local working copy ─────────────────────────────────
    safe_name = f"{uuid.uuid4().hex}_{job.source_original_filename or job.file_name}"
    restored_path = str(UPLOAD_DIR / safe_name)
    try:
        Path(restored_path).write_bytes(restored_bytes)
        logger.info(f"[DurableSource] Restored {len(restored_bytes)} bytes to {restored_path} for job {job.id}")
    except Exception as write_err:
        raise StorageUnavailableError(f"Cannot write restored source to local storage: {write_err}") from write_err

    return restored_path


def _mark_permanent_failure(
    db: Session,
    job: IngestionJob,
    error_code: str,
    message: str,
) -> None:
    """Update job to FAILED/PERMANENT_FAILURE without destroying existing partial outputs."""
    job.status = "FAILED"
    job.failed_step = "SOURCE_RESTORATION"
    job.error_code = error_code
    job.error_message = message
    job.recovery_status = "PERMANENT_FAILURE"
    job.failed_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(job)
    logger.error(f"[DurableSource] PERMANENT_FAILURE job={job.id} code={error_code}")


def process_ingestion(
    db: Session,
    file_path: str,
    file_name: str,
    file_type: str,
    source_type: str,
    file_size: int,
    user_id: Optional[uuid.UUID] = None,
    file_bytes: Optional[bytes] = None,
    content_type: Optional[str] = None,
    execute_sync: bool = True,
) -> IngestionJob:
    """
    Execute the full ingestion pipeline synchronously for a new upload.

    M15.7.1: Accepts optional file_bytes and content_type to enable durable
    source storage before pipeline execution. If file_bytes is not provided,
    the source is read from file_path for durable storage.
    """
    job = IngestionJob(
        file_name=file_name,
        source_type=source_type,
        file_type=file_type,
        file_size_bytes=file_size,
        status="QUEUED",
        uploaded_by=user_id,
        retry_count=0,
        max_retry_count=3,
        recovery_status="NONE",
    )
    db.add(job)
    db.commit()
    db.refresh(job)

    # ── M15.7.1: Store source durably BEFORE pipeline executes ──────────
    # This ensures the durable copy is available if the pipeline fails and
    # a retry is requested later.
    try:
        raw_bytes = file_bytes
        if raw_bytes is None:
            raw_bytes = Path(file_path).read_bytes()
        _store_source_durably(
            db=db,
            job=job,
            file_bytes=raw_bytes,
            original_filename=file_name,
            content_type=content_type or "application/octet-stream",
        )
    except Exception as store_err:
        # Non-fatal: log and continue
        logger.warning(f"[DurableSource] Durable store failed for job {job.id}: {store_err}")

    if execute_sync:
        return execute_pipeline(db, job, file_path)
    return job


def retry_ingestion_job(
    db: Session,
    job_id: uuid.UUID,
    user_id: Optional[uuid.UUID] = None,
) -> IngestionJob:
    """
    Re-runs an eligible failed or partial ingestion job safely.

    M15.7.1 Critical Retry Order:
        1. Lock job (caller must already hold PROCESSING status)
        2. Validate retry eligibility
        3. Verify / restore durable source   ← BEFORE any destructive action
        4. Verify SHA-256 integrity
        5. ONLY THEN: cleanup_job_outputs()  ← destructive
        6. Re-execute pipeline

    This ordering prevents the previous bug where cleanup_job_outputs()
    destroyed partial outputs BEFORE verifying the source was restorable,
    leaving the job in an unrecoverable state.
    """
    job = db.query(IngestionJob).filter(IngestionJob.id == job_id, IngestionJob.is_deleted == False).first()
    if not job:
        raise ValueError(f"Ingestion job {job_id} not found.")

    if job.status not in ("FAILED", "COMPLETED_PARTIAL", "PROCESSING"):
        raise ValueError(f"Job status '{job.status}' is not eligible for retry.")

    if (job.retry_count or 0) >= (job.max_retry_count or 3) and job.recovery_status in ("EXHAUSTED", "PERMANENT_FAILURE"):
        raise ValueError(f"Job {job_id} has exhausted its maximum retries ({job.max_retry_count}).")

    # ── Step 1: Increment retry counter & mark PROCESSING ──────────────
    # Note: The API layer has already atomically transitioned status to PROCESSING.
    # We only update the retry metadata here.
    job.retry_count = (job.retry_count or 0) + 1
    job.last_retry_at = datetime.now(timezone.utc)
    job.recovery_status = "NONE"
    job.failed_step = None
    job.error_code = None
    job.error_message = None
    db.commit()
    db.refresh(job)

    # ── Step 2: Verify & restore durable source BEFORE cleanup ──────────
    # CRITICAL: restore_source_for_job() must be called here, BEFORE
    # cleanup_job_outputs(), so that if restoration fails, the job's
    # existing partial outputs are NOT destroyed.
    try:
        file_path = restore_source_for_job(db, job)
    except (StorageKeyNotFoundError, StoragePermissionError, ValueError) as perm_err:
        # Permanent failure — source cannot be recovered; partial outputs are preserved
        logger.error(f"[Retry] Permanent source failure for job {job_id}: {perm_err}")
        # job was already marked PERMANENT_FAILURE by restore_source_for_job
        db.refresh(job)
        raise FileNotFoundError(f"Source restoration permanently failed for job {job_id}: {perm_err}") from perm_err
    except StorageUnavailableError as trans_err:
        # Transient failure — mark RETRYABLE but do NOT cleanup outputs
        job.status = "FAILED"
        job.failed_step = "SOURCE_RESTORATION"
        job.error_code = "SOURCE_STORAGE_UNAVAILABLE"
        job.error_message = f"Storage temporarily unavailable during source restoration. Retry later."
        job.recovery_status = "RETRYABLE"
        job.failed_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(job)
        logger.warning(f"[Retry] Transient storage failure for job {job_id}: {trans_err}")
        raise

    # ── Step 3: ONLY NOW perform idempotent output cleanup ───────────────
    # Source is verified/restored; safe to destroy previous partial outputs.
    cleanup_job_outputs(db, job.id)

    # ── Step 4: Re-execute pipeline on verified source ───────────────────
    return execute_pipeline(db, job, file_path)



# ── Structured field extraction ─────────────────────────────────────────

# Common field name patterns that map to entity types
STRUCTURED_FIELD_MAP = {
    "PHONE": [
        "phone", "phone_number", "mobile", "contact", "caller",
        "callee", "calling_number", "called_number",
    ],
    "PERSON": [
        "name", "full_name", "person", "suspect", "victim",
        "complainant", "witness", "caller_name", "callee_name",
        "owner", "owner_name",
    ],
    "LOCATION": [
        "location", "address", "city", "district", "state",
        "place", "area", "locality",
    ],
    "VEHICLE": [
        "vehicle", "vehicle_number", "registration", "reg_number",
        "registration_number", "plate_number",
    ],
    "DATE": [
        "date", "timestamp", "time", "datetime", "occurrence_date",
        "reported_date", "incident_date",
    ],
}


def _extract_structured_fields(
    fields: dict,
    job_id: uuid.UUID,
    row_number: int,
) -> list[EntityCandidate]:
    """Extract entity candidates from structured CSV/JSON fields."""
    candidates = []

    for entity_type, field_names in STRUCTURED_FIELD_MAP.items():
        for field_name in field_names:
            value = fields.get(field_name)
            if value and isinstance(value, str) and value.strip():
                candidates.append(EntityCandidate(
                    ingestion_job_id=job_id,
                    entity_type=entity_type,
                    raw_text=value.strip(),
                    normalized_value=normalize_entity(entity_type, value.strip()),
                    confidence=None,
                    source_row=row_number,
                    extraction_method="structured_field",
                ))

    return candidates
