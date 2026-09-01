"""
Pydantic schemas for the ingestion pipeline API.
"""
from pydantic import BaseModel, ConfigDict
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
    FAILED = "FAILED"


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
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class IngestionJobDetailResponse(IngestionJobResponse):
    """Detailed response including extracted entities."""
    entities: List[EntityCandidateResponse] = []
