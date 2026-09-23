"""
SQLAlchemy models for the ingestion pipeline.

IngestionJob: Tracks each file upload and processing lifecycle.
EntityCandidate: Stores NLP-extracted entity mentions with provenance.
"""
import uuid
from sqlalchemy import Column, String, Integer, BigInteger, Float, Text, DateTime, ForeignKey, JSON
from sqlalchemy import Uuid as UUID
from sqlalchemy.orm import relationship
from app.models.base import BaseModel


class IngestionJob(BaseModel):
    """
    Represents a single file ingestion + processing job.
    Lifecycle: QUEUED → PROCESSING → PARSED → EXTRACTED → COMPLETED | COMPLETED_PARTIAL | FAILED

    Status semantics:
        COMPLETED         — All pipeline steps succeeded, including full vector indexing
                            (or the document contained no indexable text).
        COMPLETED_PARTIAL — Entity/relationship extraction succeeded; vector indexing was
                            only partially successful (some chunks failed). RAG coverage
                            may be incomplete.
        FAILED            — A critical pipeline step failed (parsing, extraction, or
                            complete vector-indexing failure). Entity/relationship data
                            created before the failure point is preserved.
    """
    __tablename__ = "ingestion_jobs"

    file_name = Column(String(500), nullable=False)
    source_type = Column(String(100), nullable=False)  # FIR, CDR, POLICE_REPORT, etc.
    file_type = Column(String(20), nullable=False)      # pdf, csv, json, txt
    file_size_bytes = Column(Integer, nullable=True)
    status = Column(String(50), nullable=False, default="QUEUED", index=True)
    error_message = Column(Text, nullable=True)
    record_count = Column(Integer, nullable=True)       # pages for PDF, rows for CSV
    entity_count = Column(Integer, nullable=True)       # populated after extraction
    chunk_count = Column(Integer, nullable=True)        # DocumentChunk rows written to pgvector (Step 6)
    uploaded_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)

    # Async Pipeline Progress fields (M15.8)
    current_step = Column(String(100), nullable=True)    # Active pipeline step for live progress display
    relationship_count = Column(Integer, nullable=True)  # Populated after relationship extraction
    progress_detail = Column(JSON, nullable=True)        # Structured progress metadata e.g. {"parsed_pages": 3, "total_pages": 5}

    # Recovery and Reliability fields (M15.7)
    failed_step = Column(String(100), nullable=True)
    error_code = Column(String(100), nullable=True)
    retry_count = Column(Integer, nullable=False, default=0)
    max_retry_count = Column(Integer, nullable=False, default=3)
    last_retry_at = Column(DateTime(timezone=True), nullable=True)
    next_retry_at = Column(DateTime(timezone=True), nullable=True)
    failed_at = Column(DateTime(timezone=True), nullable=True)
    recovery_status = Column(String(50), nullable=False, default="NONE", index=True)

    # Durable Source Storage fields (M15.7.1)
    # These fields record the durable storage reference for the original source file.
    # All nullable for backward compatibility with pre-M15.7.1 ingestion jobs.
    # SECURITY: DO NOT store signed URLs, tokens, or secrets here — only the storage OBJECT KEY.
    source_storage_provider = Column(String(50), nullable=True)    # 'local' | 'supabase'
    source_storage_key = Column(String(1000), nullable=True)        # e.g. ingestion/{job_id}/source/{filename}
    source_original_filename = Column(String(500), nullable=True)   # original user-provided filename
    source_content_type = Column(String(200), nullable=True)        # MIME type
    source_size_bytes = Column(BigInteger, nullable=True)           # byte count of original source
    source_sha256 = Column(String(64), nullable=True)               # hex SHA-256 checksum
    source_storage_bucket = Column(String(200), nullable=True)      # bucket name (Supabase / S3)
    source_uploaded_at = Column(DateTime(timezone=True), nullable=True)  # when durable upload completed

    # Relationships
    uploader = relationship("User")
    entity_candidates = relationship("EntityCandidate", back_populates="ingestion_job", cascade="all, delete-orphan")


class EntityCandidate(BaseModel):
    """
    An NLP-extracted entity mention with full provenance.
    This is an ENTITY CANDIDATE, NOT a canonical/resolved entity.
    Entity Resolution belongs to a later milestone.
    """
    __tablename__ = "entity_candidates"

    ingestion_job_id = Column(UUID(as_uuid=True), ForeignKey("ingestion_jobs.id"), nullable=False, index=True)
    entity_type = Column(String(50), nullable=False, index=True)  # PERSON, ORGANIZATION, LOCATION, PHONE, VEHICLE, DATE
    raw_text = Column(String(1000), nullable=False)
    normalized_value = Column(String(1000), nullable=True)
    confidence = Column(Float, nullable=True)           # null if extractor doesn't provide it
    source_page = Column(Integer, nullable=True)        # page number for PDFs
    source_row = Column(Integer, nullable=True)         # row number for CSVs
    start_offset = Column(Integer, nullable=True)       # character offset in source text
    end_offset = Column(Integer, nullable=True)         # character offset in source text
    extraction_method = Column(String(50), nullable=False)  # spacy_ner, regex, structured_field

    # Resolution fields
    resolved_to_id = Column(UUID(as_uuid=True), ForeignKey("canonical_entities.id"), nullable=True, index=True)
    resolution_status = Column(String(50), nullable=False, default="UNRESOLVED", index=True) # UNRESOLVED, REVIEW_REQUIRED, RESOLVED, REJECTED, AUTO_MATCHED
    resolution_score = Column(Float, nullable=True)
    resolution_evidence = Column(JSON, nullable=True)

    # Relationships
    ingestion_job = relationship("IngestionJob", back_populates="entity_candidates")
    resolved_to = relationship("CanonicalEntity", back_populates="candidates")
