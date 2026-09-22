"""
Pydantic schemas for the ingestion pipeline API.
"""
from pydantic import BaseModel, ConfigDict, field_validator, computed_field
from typing import Optional, List
from datetime import datetime
from uuid import UUID
from enum import Enum


class JobStatus(str, Enum):
    QUEUED = "QUEUED"
    PROCESSING = "PROCESSING"
    PARSED = "PARSED"
    EXTRACTED = "EXTRACTED"
    COMPLETED = "COMPLETED"
    COMPLETED_PARTIAL = "COMPLETED_PARTIAL"
    FAILED = "FAILED"


class RecoveryStatus(str, Enum):
    NONE = "NONE"
    RETRYABLE = "RETRYABLE"
    EXHAUSTED = "EXHAUSTED"
    PERMANENT_FAILURE = "PERMANENT_FAILURE"
    RECOVERED = "RECOVERED"


class SourceType(str, Enum):
    FIR = "FIR"
    POLICE_REPORT = "POLICE_REPORT"
    CDR = "CDR"
    FINANCIAL_TRANSACTION = "FINANCIAL_TRANSACTION"
    SURVEILLANCE_REPORT = "SURVEILLANCE_REPORT"
    SOCIAL_MEDIA = "SOCIAL_MEDIA"
    CRIMINAL_HISTORY = "CRIMINAL_HISTORY"
    INTELLIGENCE_REPORT = "INTELLIGENCE_REPORT"
    OTHER = "OTHER"


# ── Response schemas ────────────────────────────────────────────────────

class EntityCandidateResponse(BaseModel):
    """API response for a single extracted entity candidate."""
    id: UUID
    entity_type: str
    raw_text: str
    normalized_value: Optional[str] = None
    confidence: Optional[float] = None
    source_page: Optional[int] = None
    source_row: Optional[int] = None
    start_offset: Optional[int] = None
    end_offset: Optional[int] = None
    extraction_method: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class IngestionJobResponse(BaseModel):
    """API response for an ingestion job."""
    id: UUID
    file_name: str
    source_type: str
    file_type: str
    file_size_bytes: Optional[int] = None
    status: str
    error_message: Optional[str] = None
    record_count: Optional[int] = None
    entity_count: Optional[int] = None
    chunk_count: Optional[int] = None   # DocumentChunk rows written to pgvector (Step 6)
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    # Recovery and Reliability fields (M15.7)
    failed_step: Optional[str] = None
    error_code: Optional[str] = None
    retry_count: int = 0
    max_retry_count: int = 3
    last_retry_at: Optional[datetime] = None
    next_retry_at: Optional[datetime] = None
    failed_at: Optional[datetime] = None
    recovery_status: str = "NONE"

    # Durable Source Storage fields (M15.7.1)
    # NOTE: source_storage_key is intentionally excluded from the response
    # to avoid leaking internal storage paths. Expose only derived/safe fields.
    source_storage_provider: Optional[str] = None
    source_has_durable_backup: Optional[bool] = None   # derived: True if source_storage_key is set
    source_sha256_prefix: Optional[str] = None          # first 12 chars for UI display
    source_size_bytes: Optional[int] = None
    source_uploaded_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

    @classmethod
    def model_validate(cls, obj, *args, **kwargs):
        """Override to derive computed fields from ORM object."""
        instance = super().model_validate(obj, *args, **kwargs)
        # Derive has_durable_backup from source_storage_key (not exposed directly)
        if hasattr(obj, 'source_storage_key'):
            instance.source_has_durable_backup = bool(obj.source_storage_key)
        # Derive sha256_prefix for display
        if hasattr(obj, 'source_sha256') and obj.source_sha256:
            instance.source_sha256_prefix = obj.source_sha256[:12] + "..."
        return instance


class IngestionJobDetailResponse(IngestionJobResponse):
    """Detailed response including extracted entities."""
    entities: List[EntityCandidateResponse] = []
