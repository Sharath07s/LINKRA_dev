"""
M1.14 — Report Schemas

Every field has an explicit source_type to distinguish:
  "observed"           — direct PostgreSQL record
  "structural_analysis"— derived from Neo4j graph structure
  "prediction"         — topology-based, NOT a confirmed relationship
  "ai_generated"       — LLM synthesis, explicitly labeled
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


# ──────────────────────────────────────────────────────────────────
# Provenance
# ──────────────────────────────────────────────────────────────────

class ReportProvenance(BaseModel):
    ingestion_job_id: Optional[str] = None
    source_type: Optional[str] = None       # FIR, CDR, POLICE_REPORT, etc.
    file_name: Optional[str] = None
    file_type: Optional[str] = None
    page: Optional[int] = None
    row: Optional[int] = None


# ──────────────────────────────────────────────────────────────────
# Investigation Summary
# ──────────────────────────────────────────────────────────────────

class ReportInvestigationSummary(BaseModel):
    investigation_id: str
    crime_id: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    summary: Optional[str] = None
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    source_type: str = "observed"


# ──────────────────────────────────────────────────────────────────
# Entities
# ──────────────────────────────────────────────────────────────────

class ReportEntity(BaseModel):
    entity_id: str
    name: str
    entity_type: str
    aliases: Optional[List[str]] = Field(default_factory=list)
    attributes: Optional[Dict[str, Any]] = Field(default_factory=dict)
    source_type: str = "observed"


# ──────────────────────────────────────────────────────────────────
# Relationships
# ──────────────────────────────────────────────────────────────────

class ReportRelationship(BaseModel):
    source_entity_id: str
    source_entity_name: str
    target_entity_id: str
    target_entity_name: str
    relationship_type: str
    confidence: float
    extraction_method: str
    event_timestamp: Optional[str] = None
    provenance: Optional[ReportProvenance] = None
    source_type: str = "observed"


# ──────────────────────────────────────────────────────────────────
# Evidence / Provenance
# ──────────────────────────────────────────────────────────────────

class ReportEvidence(BaseModel):
    evidence_type: str                      # ENTITY_EXTRACTION, RELATIONSHIP_EXTRACTION
    title: str
    description: Optional[str] = None
    timestamp: Optional[str] = None
    provenance: Optional[ReportProvenance] = None
    source_type: str = "observed"


# ──────────────────────────────────────────────────────────────────
# Graph / Structural Analytics
# ──────────────────────────────────────────────────────────────────

class ReportGraphEntitySummary(BaseModel):
    entity_id: str
    entity_name: str
    degree: int = 0
    in_degree: int = 0
    out_degree: int = 0
    relationship_distribution: List[Dict[str, Any]] = Field(default_factory=list)
    source_type: str = "structural_analysis"


class ReportGraphSummary(BaseModel):
    total_entities_in_investigation: int = 0
    entity_summaries: List[ReportGraphEntitySummary] = Field(default_factory=list)
    source_type: str = "structural_analysis"


# ──────────────────────────────────────────────────────────────────
# Anomalies
# ──────────────────────────────────────────────────────────────────

class ReportAnomaly(BaseModel):
    anomaly_id: str
    entity_id: str
    entity_name: str
    anomaly_type: str
    severity: str
    score: float
    observed_value: float
    baseline_value: float
    reason: str
    interpretation: Optional[str] = None
    # IMPORTANT: anomaly is a statistical signal, NOT proof of criminal activity
    disclaimer: str = "This is a structural graph anomaly based on statistical thresholds. It does not constitute evidence of criminal activity."
    source_type: str = "structural_analysis"


# ──────────────────────────────────────────────────────────────────
# Potential Links
# ──────────────────────────────────────────────────────────────────

class ReportPotentialLink(BaseModel):
    source_entity_id: str
    source_entity_name: str
    target_entity_id: str
    target_entity_name: str
    target_entity_type: str
    score: float
    common_neighbors: int
    jaccard_similarity: float
    preferential_attachment_normalized: float
    reason: str
    # IMPORTANT: prediction is topology-based, NOT a confirmed relationship
    disclaimer: str = "Based strictly on shared graph topology. NOT a confirmed relationship. NOT evidence of criminal activity."
    source_type: str = "prediction"


# ──────────────────────────────────────────────────────────────────
# AI-Generated Section
# ──────────────────────────────────────────────────────────────────

class ReportAISection(BaseModel):
    narrative: str
    provider: str
    grounded: bool = True
    disclaimer: str = (
        "This section is an AI-generated analytical summary. It is derived strictly "
        "from the verified evidence, graph analytics, and provenance data provided above. "
        "It does not introduce new intelligence, confirm predictions, or constitute "
        "legal evidence of any criminal activity."
    )
    source_type: str = "ai_generated"


# ──────────────────────────────────────────────────────────────────
# Generation Metadata
# ──────────────────────────────────────────────────────────────────

class ReportGenerationMetadata(BaseModel):
    generated_at: str
    report_version: str = "1.0"
    investigation_id: str
    entity_count: int
    relationship_count: int
    evidence_count: int
    anomaly_count: int
    potential_link_count: int
    ai_generated: bool = False
    data_sources: List[str] = Field(default_factory=lambda: ["postgresql", "neo4j"])


# ──────────────────────────────────────────────────────────────────
# Top-Level Report Response
# ──────────────────────────────────────────────────────────────────

class ReportResponse(BaseModel):
    investigation: ReportInvestigationSummary
    entities: List[ReportEntity] = Field(default_factory=list)
    relationships: List[ReportRelationship] = Field(default_factory=list)
    evidence: List[ReportEvidence] = Field(default_factory=list)
    graph_summary: ReportGraphSummary = Field(default_factory=ReportGraphSummary)
    anomalies: List[ReportAnomaly] = Field(default_factory=list)
    potential_links: List[ReportPotentialLink] = Field(default_factory=list)
    ai_section: Optional[ReportAISection] = None
    metadata: ReportGenerationMetadata
    limitations: List[str] = Field(default_factory=list)
