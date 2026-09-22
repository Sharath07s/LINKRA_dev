from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import List, Dict, Any
from pydantic import BaseModel
import uuid
from datetime import datetime

from app.api import deps
from app.models.user import User
from app.models.ingestion import EntityCandidate
from app.models.resolution import CanonicalEntity
from app.models.event_audit_log import EventAuditLog
from app.ai.neo4j.intelligence import neo4j_intelligence
from app.nlp.resolution.engine import get_possible_matches

router = APIRouter()

class PossibleMatch(BaseModel):
    canonical_entity_id: str
    name: str
    match_score: float

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
    possible_matches: List[PossibleMatch] = []
    
    class Config:
        from_attributes = True

class ConfirmMatchRequest(BaseModel):
    canonical_entity_id: str

class CreateEntityRequest(BaseModel):
    name: str

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
                
        # Generate possible matches dynamically
        matches = get_possible_matches(db, c)
                
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
            resolution_evidence=c.resolution_evidence,
            possible_matches=[PossibleMatch(**m) for m in matches]
        ))
    return response

@router.post("/{candidate_id}/confirm")
def confirm_match(
    candidate_id: str,
    payload: ConfirmMatchRequest,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.RoleChecker(["OFFICER", "ADMIN", "EXECUTIVE"]))
):
    """Approve a proposed match, linking the candidate to the canonical entity."""
    try:
        cand_uuid = uuid.UUID(candidate_id)
        canon_uuid = uuid.UUID(payload.canonical_entity_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid UUID")
        
    candidate = db.query(EntityCandidate).filter(EntityCandidate.id == cand_uuid).first()
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
        
    if candidate.resolution_status != "REVIEW_REQUIRED":
        raise HTTPException(status_code=400, detail="Candidate is not in review state")
        
    canonical = db.query(CanonicalEntity).filter(CanonicalEntity.id == canon_uuid).first()
    if not canonical:
        raise HTTPException(status_code=404, detail="Canonical entity not found")
        
    # Link it
    candidate.resolution_status = "RESOLVED"
    candidate.resolved_to_id = canonical.id
    
    # Audit log
    audit = EventAuditLog(
        event_id=candidate_id,
        event_type="HUMAN_REVIEW_CONFIRM",
        source=f"user:{current_user.id}",
        status="processed",
        timestamp=datetime.utcnow()
    )
    db.add(audit)
    
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
    payload: CreateEntityRequest,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.RoleChecker(["OFFICER", "ADMIN", "EXECUTIVE"]))
):
    """Explicitly create a new canonical entity from the candidate."""
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
        name=payload.name,
        aliases=[candidate.raw_text] if candidate.raw_text != payload.name else [],
        attributes={}
    )
    db.add(canonical)
    
    candidate.resolution_status = "RESOLVED"
    
    db.commit()
    db.refresh(canonical)
    
    candidate.resolved_to_id = canonical.id
    
    # Audit log
    audit = EventAuditLog(
        event_id=candidate_id,
        event_type="HUMAN_REVIEW_CREATE",
        source=f"user:{current_user.id}",
        status="processed",
        timestamp=datetime.utcnow()
    )
    db.add(audit)
    
    neo4j_intelligence.sync_canonical_entity(
        entity_id=str(canonical.id),
        entity_type=canonical.entity_type,
        properties={"name": canonical.name, "aliases": canonical.aliases}
    )
    
    db.commit()
    return {"status": "success", "message": "New entity created"}

@router.post("/{candidate_id}/reject")
def reject_match(
    candidate_id: str,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.RoleChecker(["OFFICER", "ADMIN", "EXECUTIVE"]))
):
    """Reject a match. Marks candidate as REJECTED."""
    try:
        cand_uuid = uuid.UUID(candidate_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid UUID")
        
    candidate = db.query(EntityCandidate).filter(EntityCandidate.id == cand_uuid).first()
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
        
    if candidate.resolution_status != "REVIEW_REQUIRED":
        raise HTTPException(status_code=400, detail="Candidate is not in review state")
        
    # Mark rejected
    candidate.resolution_status = "REJECTED"
    candidate.resolved_to_id = None
    
    # Audit log
    audit = EventAuditLog(
        event_id=candidate_id,
        event_type="HUMAN_REVIEW_REJECT",
        source=f"user:{current_user.id}",
        status="processed",
        timestamp=datetime.utcnow()
    )
    db.add(audit)
    
    db.commit()
    return {"status": "success", "message": "Match rejected"}
