"""
SQLAlchemy models for the ingestion pipeline.

IngestionJob: Tracks each file upload and processing lifecycle.
EntityCandidate: Stores NLP-extracted entity mentions with provenance.
"""
import uuid
from sqlalchemy import Column, String, Integer, Float, Text, DateTime, ForeignKey, JSON
from sqlalchemy import Uuid as UUID
from sqlalchemy.orm import relationship
from app.models.base import BaseModel


class IngestionJob(BaseModel):
    """
    Represents a single file ingestion + processing job.
    Lifecycle: QUEUED → PROCESSING → PARSED → EXTRACTED → COMPLETED | FAILED
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
