from pydantic import BaseModel, Field, UUID4
from typing import Optional, List, Dict, Any
from enum import Enum

class CopilotIntent(str, Enum):
    ENTITY_LOOKUP = "ENTITY_LOOKUP"
    RELATIONSHIP_LOOKUP = "RELATIONSHIP_LOOKUP"
    EVIDENCE_LOOKUP = "EVIDENCE_LOOKUP"
    GRAPH_EXPLORATION = "GRAPH_EXPLORATION"
    ANOMALY_EXPLANATION = "ANOMALY_EXPLANATION"
    POTENTIAL_LINK_EXPLANATION = "POTENTIAL_LINK_EXPLANATION"
    INVESTIGATION_SUMMARY = "INVESTIGATION_SUMMARY"
    COMPARISON = "COMPARISON"
    GENERAL_INTELLIGENCE_QUERY = "GENERAL_INTELLIGENCE_QUERY"
    COMMUNITY_LOOKUP = "COMMUNITY_LOOKUP"
    UNSUPPORTED_QUERY = "UNSUPPORTED_QUERY"

class CopilotQuery(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000)
    investigation_id: Optional[str] = None
    entity_id: Optional[str] = None
    conversation_id: Optional[str] = None

class CopilotCitation(BaseModel):
    type: str
    id: str
    label: str
    context: Optional[str] = None

class CopilotResponse(BaseModel):
    status: str  # ANSWERED, INSUFFICIENT_DATA, CLARIFICATION_REQUIRED, UNSUPPORTED, PROVIDER_UNAVAILABLE
    answer: str
    intent: Optional[CopilotIntent] = None
    sources: List[CopilotCitation] = Field(default_factory=list)
    evidence: List[Dict[str, Any]] = Field(default_factory=list)
    entities: List[Dict[str, Any]] = Field(default_factory=list)
    analytics: List[Dict[str, Any]] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    provider: Optional[str] = None
    grounded: bool = True
