from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import or_
import uuid

from app.api import deps
from app.models.user import User
from app.models.relationship import EntityRelationship

from app.api.deps import RoleChecker

router = APIRouter()

allow_analysts = RoleChecker(["ADMIN", "SUPERVISOR", "INVESTIGATOR", "ANALYST"])

@router.get("/entity/{entity_id}", dependencies=[Depends(allow_analysts)])
def get_entity_relationships(
    entity_id: uuid.UUID,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user)
):
    """
    Get all relationships for a given canonical entity.
    """
    relationships = db.query(EntityRelationship).filter(
        or_(
            EntityRelationship.source_entity_id == entity_id,
            EntityRelationship.target_entity_id == entity_id
        )
    ).all()
    
    # Return basic data; in production this would join with CanonicalEntity to fetch names
    result = []
    for rel in relationships:
        result.append({
            "id": str(rel.id),
            "source_entity_id": str(rel.source_entity_id),
            "target_entity_id": str(rel.target_entity_id),
            "relationship_type": rel.relationship_type,
            "confidence": rel.confidence,
            "evidence_text": rel.evidence_text,
            "extraction_method": rel.extraction_method,
            "event_timestamp": rel.event_timestamp.isoformat() if rel.event_timestamp else None,
            "ingestion_job_id": str(rel.ingestion_job_id) if rel.ingestion_job_id else None,
            "source_page": rel.source_page,
            "source_row": rel.source_row,
        })
    return {"relationships": result}
