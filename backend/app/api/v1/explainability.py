from typing import Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.api import deps
from app.schemas.graph import ExplainabilityResponse
from app.models.resolution import CanonicalEntity
from app.models.ingestion import EntityCandidate, IngestionJob
from app.models.relationship import EntityRelationship
from app.ai.neo4j.analytics import neo4j_analytics
from app.ai.neo4j.anomaly import neo4j_anomaly
from app.ai.neo4j.predictions import neo4j_predictions

router = APIRouter()

@router.get("/entity/{entity_id}", response_model=ExplainabilityResponse)
def get_entity_explainability(
    entity_id: str,
    db: Session = Depends(deps.get_db),
    current_user: Any = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get full explainability and evidence traceability for a canonical entity.
    Requires an authenticated user.
    """
    import uuid
    try:
        entity_uuid = uuid.UUID(entity_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid UUID format")

    # 1. Fetch the Entity
    entity = db.query(CanonicalEntity).filter(CanonicalEntity.id == entity_uuid).first()
    if not entity:
        raise HTTPException(status_code=404, detail="Entity not found")
        
    evidence_list = []
    
    # 2. Fetch EntityCandidates (Source Evidence)
    candidates = db.query(EntityCandidate).filter(EntityCandidate.resolved_to_id == entity.id).all()
    for candidate in candidates:
        if candidate.ingestion_job_id:
            job = db.query(IngestionJob).filter(IngestionJob.id == candidate.ingestion_job_id).first()
            if job:
                evidence_list.append({
                    "type": "ENTITY_EXTRACTION",
                    "title": f"Extracted as '{candidate.raw_text}'",
                    "timestamp": job.completed_at.isoformat() if job.completed_at else None,
                    "description": f"Extracted via {candidate.extraction_method} with {int((candidate.confidence or 1.0) * 100)}% confidence.",
                    "provenance": {
                        "ingestion_job_id": str(job.id),
                        "source_type": job.source_type,
                        "file_name": job.file_name,
                        "file_type": job.file_type,
                        "page": candidate.source_page,
                        "row": candidate.source_row
                    }
                })

    # 3. Fetch Observed Relationships
    observed_relationships = []
    rels = db.query(EntityRelationship).filter(
        or_(
            EntityRelationship.source_entity_id == entity.id,
            EntityRelationship.target_entity_id == entity.id
        )
    ).all()
    
    for rel in rels:
        # Resolve target/source name quickly for explanation
        other_id = rel.target_entity_id if str(rel.source_entity_id) == entity_id else rel.source_entity_id
        other_entity = db.query(CanonicalEntity).filter(CanonicalEntity.id == other_id).first()
        other_name = other_entity.name if other_entity else str(other_id)
        
        rel_evidence = {
            "id": str(rel.id),
            "relationship_type": rel.relationship_type,
            "connected_entity_id": str(other_id),
            "connected_entity_name": other_name,
            "confidence": rel.confidence,
            "evidence_text": rel.evidence_text,
            "extraction_method": rel.extraction_method,
            "direction": "OUTGOING" if str(rel.source_entity_id) == entity_id else "INCOMING",
            "event_timestamp": rel.event_timestamp.isoformat() if rel.event_timestamp else None,
            "provenance": None
        }
        
        if rel.ingestion_job_id:
            job = db.query(IngestionJob).filter(IngestionJob.id == rel.ingestion_job_id).first()
            if job:
                rel_evidence["provenance"] = {
                    "ingestion_job_id": str(job.id),
                    "source_type": job.source_type,
                    "file_name": job.file_name,
                    "file_type": job.file_type,
                    "page": rel.source_page,
                    "row": rel.source_row
                }
                
        observed_relationships.append(rel_evidence)

    # 4. Fetch Structural Analytics from Neo4j
    structural_analytics = {}
    try:
        degree_res = neo4j_analytics.get_entity_degree(entity_id)
        dist_res = neo4j_analytics.get_relationship_distribution(entity_id)
        structural_analytics = {
            "degree": degree_res.get("total_degree", 0),
            "in_degree": degree_res.get("in_degree", 0),
            "out_degree": degree_res.get("out_degree", 0),
            "distribution": dist_res if isinstance(dist_res, list) else dist_res.get("distribution", [])
        }
    except Exception as e:
        structural_analytics = {"error": "Failed to fetch structural analytics"}

    # 5. Fetch Anomalies from Neo4j
    anomalies = []
    try:
        anomaly_res = neo4j_anomaly.get_anomalies_for_entity(entity_id)
        if anomaly_res.get("status") == "success":
            anomalies = anomaly_res.get("anomalies", [])
    except Exception as e:
        pass # Handle gracefully if Neo4j is sparse or failing

    # 6. Fetch Potential Links from Neo4j
    potential_links = []
    try:
        pred_res = neo4j_predictions.get_potential_links_for_entity(entity_id)
        if pred_res.get("status") == "success":
            potential_links = pred_res.get("potential_links", [])
    except Exception as e:
        pass # Handle gracefully

    return {
        "entity_id": str(entity.id),
        "entity_name": entity.name,
        "evidence": evidence_list,
        "observed_relationships": observed_relationships,
        "structural_analytics": structural_analytics,
        "anomalies": anomalies,
        "potential_links": potential_links
    }
