from pydantic import BaseModel
from enum import Enum

class ConfidenceLevel(str, Enum):
    CONFIRMED = "CONFIRMED"
    INFERRED = "INFERRED"
    PREDICTED = "PREDICTED"

class EvidenceReference(BaseModel):
    # PLACEHOLDER
    source_id: str
    confidence: ConfidenceLevel
