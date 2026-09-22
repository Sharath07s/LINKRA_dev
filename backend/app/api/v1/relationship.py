from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import or_
import uuid

from app.api import deps
from app.models.user import User
from app.models.relationship import EntityRelationship
from app.models.ingestion import IngestionJob
from app.models.evidence_link import EvidenceLink
from app.models.document import DocumentChunk

from app.api.deps import RoleChecker

router = APIRouter()

allow_analysts = RoleChecker(["ADMIN", "SUPERVISOR", "INVESTIGATOR", "ANALYST", "OFFICER"])

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
    
    result = []
    for rel in relationships:
        result.append({
            "id": str(rel.id),
            "source_entity_id": str(rel.source_entity_id),
            "target_entity_id": str(rel.target_entity_id),
            "relationship_type": rel.relationship_type,
            "confidence": rel.confidence,
            "status": rel.status,
            "evidence_text": rel.evidence_text,
            "extraction_method": rel.extraction_method,
            "event_timestamp": rel.event_timestamp.isoformat() if rel.event_timestamp else None,
            "ingestion_job_id": str(rel.ingestion_job_id) if rel.ingestion_job_id else None,
            "source_page": rel.source_page,
            "source_row": rel.source_row,
        })
    return {"relationships": result}


@router.get("/{relationship_id}/evidence", dependencies=[Depends(allow_analysts)])
def get_relationship_evidence(
    relationship_id: uuid.UUID,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user)
):
    """
    Get grounded source evidence and DocumentChunk linkages for a specific relationship.
    """
    rel = db.query(EntityRelationship).filter(EntityRelationship.id == relationship_id).first()
    if not rel:
        raise HTTPException(status_code=404, detail="Relationship not found")

    job = None
    if rel.ingestion_job_id:
        job = db.query(IngestionJob).filter(IngestionJob.id == rel.ingestion_job_id).first()

    links = (
        db.query(EvidenceLink)
        .filter(EvidenceLink.relationship_id == rel.id)
        .all()
    )

    evidence_links_data = []
    for link in links:
        chunk = link.document_chunk
        chunk_meta = chunk.metadata_json if chunk and chunk.metadata_json else {}
        evidence_links_data.append({
            "evidence_link_id": str(link.id),
            "document_chunk_id": str(link.document_chunk_id),
            "quote_snippet": link.quote_snippet,
            "char_start": link.char_start,
            "char_end": link.char_end,
            "confidence": link.confidence,
            "chunk_index": chunk_meta.get("chunk_index"),
            "page_number": chunk_meta.get("page_number", rel.source_page),
            "source_filename": chunk_meta.get("source_filename", job.file_name if job else None),
        })

    return {
        "relationship_id": str(rel.id),
        "relationship_type": rel.relationship_type,
        "confidence": rel.confidence,
        "status": rel.status,
        "extraction_method": rel.extraction_method,
        "evidence_text": rel.evidence_text,
        "ingestion_job_id": str(rel.ingestion_job_id) if rel.ingestion_job_id else None,
        "source_page": rel.source_page,
        "source_row": rel.source_row,
        "source_filename": job.file_name if job else None,
        "evidence_links": evidence_links_data,
    }
