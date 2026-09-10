from typing import List, Dict, Any, Optional
from pydantic import BaseModel

class GraphNode(BaseModel):
    id: str
    label: str
    type: str
    risk: str
    rating: float
    desc: str

class GraphEdge(BaseModel):
    source: str
    target: str
    relation: str
    weight: float
    desc: str

class GraphResponse(BaseModel):
    nodes: List[GraphNode]
    edges: List[GraphEdge]
    center_entity_id: Optional[str] = None
    total_nodes: int = 0
    total_edges: int = 0

class DegreeAnalyticsResponse(BaseModel):
    total_degree: int
    in_degree: int
    out_degree: int

class CentralityNode(BaseModel):
    entity_id: str
    name: str
    type: str
    degree: int

class ShortestPathResponse(BaseModel):
    path_exists: bool
    length: int
    nodes: List[Dict[str, Any]]
    edges: List[Dict[str, Any]]

class RelationshipDistributionItem(BaseModel):
    rel_type: str
    count: int

class ComponentAnalyticsResponse(BaseModel):
    component_size: int

class AnomalyExplanation(BaseModel):
    reason: str
    metrics: Dict[str, Any]
    method: str
    interpretation: str

class AnomalySignal(BaseModel):
    anomaly_id: str
    entity_id: str
    anomaly_type: str
    severity: str
    score: float
    observed_value: float
    baseline_value: float
    reason: str
    explanation: Optional[AnomalyExplanation] = None

class AnomalyResponse(BaseModel):
    status: str
    anomalies: List[AnomalySignal]
    reason: Optional[str] = None

class PotentialLinkSignals(BaseModel):
    common_neighbors: int
    jaccard_similarity: float
    preferential_attachment_normalized: float

class PotentialLinkExplanation(BaseModel):
    reason: str
    method: str

class PotentialLink(BaseModel):
    source_entity_id: str
    target_entity_id: str
    target_entity_name: str
    target_entity_type: str
    score: float
    signals: PotentialLinkSignals
    weights: Dict[str, float]
    explanation: PotentialLinkExplanation

class PotentialLinkResponse(BaseModel):
    status: str
    potential_links: List[PotentialLink]
    reason: Optional[str] = None

class ProvenanceRecord(BaseModel):
    ingestion_job_id: str
    source_type: str
    file_name: str
    file_type: str
    page: Optional[int] = None
    row: Optional[int] = None

class ExplainableEvidence(BaseModel):
    type: str
    title: str
    provenance: Optional[ProvenanceRecord] = None
    timestamp: Optional[str] = None
    description: Optional[str] = None

class ExplainabilityResponse(BaseModel):
    entity_id: str
    entity_name: str
    evidence: List[ExplainableEvidence]
    observed_relationships: List[Dict[str, Any]]
    structural_analytics: Dict[str, Any]
    anomalies: List[AnomalySignal]
    potential_links: List[PotentialLink]

class CommunityMember(BaseModel):
    entity_id: str
    name: str
    type: str

class Community(BaseModel):
    community_id: str
    size: int
    members: List[CommunityMember]

class CommunityResponse(BaseModel):
    status: str
    message: Optional[str] = None
    algorithm: Optional[str] = "louvain"
    communities: List[Community] = []
