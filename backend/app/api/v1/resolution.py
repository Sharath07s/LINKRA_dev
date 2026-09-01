from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import List, Dict, Any
from pydantic import BaseModel
import uuid

from app.api import deps
from app.models.user import User
from app.models.ingestion import EntityCandidate
from app.models.resolution import CanonicalEntity
from app.ai.neo4j.intelligence import neo4j_intelligence

router = APIRouter()

class ResolutionReviewResponse(BaseModel):
    candidate_id: str
    entity_type: str
    raw_text: str
    normalized_value: str
    confidence: float | None
    source_info: str
    proposed_canonical_id: str | None
    proposed_canonical_name: str | None
    resolution_score: float | None
    resolution_evidence: dict | None
    
    class Config:
        from_attributes = True

@router.get("/review-queue", response_model=List[ResolutionReviewResponse])
def get_review_queue(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.RoleChecker(["OFFICER", "ADMIN", "EXECUTIVE"])),
    skip: int = 0,
    limit: int = 50
):
    """
    Get all entity candidates that require manual review.
    """
    candidates = (
        db.query(EntityCandidate)
        .filter(EntityCandidate.resolution_status == "REVIEW_REQUIRED")
        .offset(skip)
        .limit(limit)
        .all()
    )
    
    response = []
    for c in candidates:
        source_info = f"Job {c.ingestion_job_id}"
        if c.source_page:
            source_info += f" Page {c.source_page}"
        elif c.source_row:
            source_info += f" Row {c.source_row}"
            
        proposed_id = str(c.resolved_to_id) if c.resolved_to_id else None
        proposed_name = None
        if proposed_id:
            can = db.query(CanonicalEntity).filter(CanonicalEntity.id == c.resolved_to_id).first()
            if can:
                proposed_name = can.name
                
        response.append(ResolutionReviewResponse(
            candidate_id=str(c.id),
            entity_type=c.entity_type,
            raw_text=c.raw_text,
            normalized_value=c.normalized_value or "",
            confidence=c.confidence,
            source_info=source_info,
            proposed_canonical_id=proposed_id,
            proposed_canonical_name=proposed_name,
            resolution_score=c.resolution_score,
            resolution_evidence=c.resolution_evidence
        ))
    return response

@router.post("/{candidate_id}/approve")
def approve_match(
    candidate_id: str,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.RoleChecker(["OFFICER", "ADMIN", "EXECUTIVE"]))
):
    """Approve a proposed match, linking the candidate to the canonical entity."""
    try:
        cand_uuid = uuid.UUID(candidate_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid UUID")
        
    candidate = db.query(EntityCandidate).filter(EntityCandidate.id == cand_uuid).first()
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
        
    if candidate.resolution_status != "REVIEW_REQUIRED" or not candidate.resolved_to_id:
        raise HTTPException(status_code=400, detail="Candidate is not in review state with a proposed match")
        
    canonical = db.query(CanonicalEntity).filter(CanonicalEntity.id == candidate.resolved_to_id).first()
    if not canonical:
        raise HTTPException(status_code=404, detail="Proposed canonical entity not found")
        
    # Link it
    candidate.resolution_status = "RESOLVED"
    
    # Add alias if it's new
    raw = candidate.raw_text
    aliases = canonical.aliases or []
    if raw not in aliases and raw != canonical.name:
        aliases.append(raw)
        canonical.aliases = aliases
        # Sync to neo4j
        neo4j_intelligence.sync_canonical_entity(
            entity_id=str(canonical.id),
            entity_type=canonical.entity_type,
            properties={"name": canonical.name, "aliases": canonical.aliases}
        )
        
    db.commit()
    return {"status": "success", "message": "Match approved"}

@router.post("/{candidate_id}/create-entity")
def create_new_entity(
    candidate_id: str,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.RoleChecker(["OFFICER", "ADMIN", "EXECUTIVE"]))
):
    """Reject a match and explicitly create a new canonical entity from the candidate."""
    try:
        cand_uuid = uuid.UUID(candidate_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid UUID")
        
    candidate = db.query(EntityCandidate).filter(EntityCandidate.id == cand_uuid).first()
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
        
    if candidate.resolution_status != "REVIEW_REQUIRED":
        raise HTTPException(status_code=400, detail="Candidate is not in review state")
        
    # Create new
    canonical = CanonicalEntity(
        entity_type=candidate.entity_type,
        name=candidate.normalized_value or candidate.raw_text,
        aliases=[candidate.raw_text] if candidate.raw_text != candidate.normalized_value else [],
        attributes={}
    )
    db.add(canonical)
    db.commit()
    db.refresh(canonical)
    
    neo4j_intelligence.sync_canonical_entity(
        entity_id=str(canonical.id),
        entity_type=canonical.entity_type,
        properties={"name": canonical.name, "aliases": canonical.aliases}
    )
    
    candidate.resolution_status = "RESOLVED"
    candidate.resolved_to_id = canonical.id
    db.commit()
    return {"status": "success", "message": "New entity created"}
