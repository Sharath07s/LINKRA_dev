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


def process_ingestion(
    db: Session,
    file_path: str,
    file_name: str,
    file_type: str,
    source_type: str,
    file_size: int,
    user_id: Optional[uuid.UUID] = None,
) -> IngestionJob:
    """
    Execute the full ingestion pipeline synchronously.

    Steps:
    1. Create IngestionJob record
    2. Parse the file into ParsedDocument/ParsedPage objects
    3. Run NLP (spaCy + regex) and LLM entity extraction
    4. Entity resolution → CanonicalEntity (PostgreSQL)
    5. Relationship extraction → EntityRelationship (PostgreSQL + Neo4j)
    6. RAG vector indexing → DocumentChunk (pgvector)

    Step 6 is wrapped in its own try/except block so that a vector-indexing
    failure never rolls back entity/relationship/Neo4j work already committed
    in Steps 3–5.

    Args:
        db: SQLAlchemy session
        file_path: Path to the saved uploaded file
        file_name: Original filename
        file_type: Normalized extension (pdf, csv, json, txt)
        source_type: Domain source type (FIR, CDR, etc.)
        file_size: File size in bytes
        user_id: UUID of the uploading user

    Returns:
        The completed IngestionJob record.
    """
    # ── Step 1: Create job record ───────────────────────────────────────
    job = IngestionJob(
        file_name=file_name,
        source_type=source_type,
        file_type=file_type,
        file_size_bytes=file_size,
        status="QUEUED",
        uploaded_by=user_id,
    )
    db.add(job)
    db.commit()
    db.refresh(job)

    try:
        # ── Step 2: Parse ───────────────────────────────────────────────
        job.status = "PROCESSING"
        job.started_at = datetime.now(timezone.utc)
        db.commit()

        parser = PARSER_MAP.get(file_type)
        if parser is None:
            raise ValueError(f"No parser available for file type: {file_type}")

        parsed: ParsedDocument = parser(file_path)

        job.status = "PARSED"
        job.record_count = parsed.record_count
        db.commit()

        # ── Step 3: NLP Extraction ──────────────────────────────────────
        all_candidates: list[EntityCandidate] = []

        for page in parsed.pages:
            if not page.text.strip():
                continue

            # Calculate character offset for multi-page provenance
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

            # Also extract structured fields from CSV/JSON metadata
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
                    # Deduplicate against spaCy/Regex
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
        db.commit()

        # ── Step 4: Persist candidates ──────────────────────────────────
        if all_candidates:
            for candidate in all_candidates:
                # Build context from other candidates on the same page/row
                context = ResolutionContext()
                
                # We only collect context if this is a PERSON, ORG, LOC
                # Because phones/vehicles match exactly on themselves.
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
            from app.nlp.relationship import extract_relationships_for_page
            for page in parsed.pages:
                page_candidates = [
                    c for c in all_candidates 
                    if c.source_page == page.page_number or c.source_row == page.page_number
                ]
                extract_relationships_for_page(db, job, page, page_candidates)

        job.entity_count = len(all_candidates)

        # ── Step 6: RAG Vector Indexing ──────────────────────────────────
        # Deliberately isolated from the main try/except so that vector-
        # indexing failures never revert already-committed entity/relationship
        # work. The job is still marked COMPLETED even if indexing fails,
        # but chunk_count will remain 0 and a WARNING is logged.
        chunk_count = 0
        try:
            from app.ai.rag.vector_search import VectorStore
            # Instantiate once — the embedding model (~90 MB) is loaded here,
            # not inside the per-chunk loop.
            vs = VectorStore()
            doc_total_pages = parsed.record_count

            for page in parsed.pages:
                if not page.text.strip():
                    continue

                # Split page text into sub-page chunks.
                # Short pages (< chunk_size) naturally produce a single chunk.
                raw_chunks = _get_chunk_splitter().split_text(page.text)
                total_chunks_on_page = len(raw_chunks)

                for chunk_index, chunk_text in enumerate(raw_chunks):
                    if not chunk_text.strip():
                        continue

                    # Build metadata from data already available in scope.
                    # Do NOT invent FIR numbers, station names, or districts —
                    # those are not reliably structured at this stage.
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

                    # Preserve any structured metadata already on the page
                    # (e.g., page_index from PDF parser, fields from CSV parser).
                    # Only copy safe scalar types to avoid deep-nesting issues.
                    for k, v in page.metadata.items():
                        if isinstance(v, (str, int, float, bool)) and k not in metadata:
                            metadata[k] = v

                    success = vs.index_document(
                        source_id=file_name,
                        text=chunk_text,
                        metadata=metadata,
                    )
                    if success:
                        chunk_count += 1
                    else:
                        logger.warning(
                            f"Ingestion job {job.id} ({file_name}): "
                            f"index_document() returned False for page "
                            f"{page.page_number} chunk {chunk_index}."
                        )

            logger.info(
                f"Ingestion job {job.id} ({file_name}): "
                f"vector indexing complete — {chunk_count} chunk(s) stored in pgvector."
            )

            # ── Step 7: Phase 2 Evidence Linking ─────────────────────────────
            # Ground persisted EntityRelationship rows to supporting DocumentChunks
            if chunk_count > 0:
                try:
                    from app.ingestion.evidence_linker import link_evidence_for_job
                    link_evidence_for_job(db, job)
                except Exception as link_err:
                    logger.warning(
                        f"Ingestion job {job.id} ({file_name}): "
                        f"Evidence linking encountered an error: {link_err}"
                    )
        except Exception as vec_err:
            logger.warning(
                f"Ingestion job {job.id} ({file_name}): "
                f"vector indexing failed — entity/relationship data is preserved. "
                f"Error: {vec_err}"
            )
            # chunk_count stays 0; job is still marked COMPLETED below.

        job.chunk_count = chunk_count
        job.status = "COMPLETED"
        job.completed_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(job)

        logger.info(
            f"Ingestion job {job.id} completed: "
            f"{job.record_count} records, {job.entity_count} entities extracted, "
            f"{chunk_count} vector chunk(s) indexed."
        )

    except Exception as e:
        logger.error(f"Ingestion job {job.id} failed: {e}")
        job.status = "FAILED"
        job.error_message = str(e)[:2000]
        job.completed_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(job)

    return job


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
