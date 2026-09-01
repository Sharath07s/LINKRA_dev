from sqlalchemy import Column, String, Float, Integer, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy import Uuid as UUID
from sqlalchemy.orm import relationship
from app.models.base import BaseModel

class EntityRelationship(BaseModel):
    """
    An evidence-backed relationship discovered between two canonical entities.
    """
    __tablename__ = "entity_relationships"

    source_entity_id = Column(UUID(as_uuid=True), ForeignKey("canonical_entities.id"), index=True, nullable=False)
    target_entity_id = Column(UUID(as_uuid=True), ForeignKey("canonical_entities.id"), index=True, nullable=False)
    
    relationship_type = Column(String(100), nullable=False, index=True) # COMMUNICATED_WITH, MET_WITH, etc.
    confidence = Column(Float, nullable=False)
    extraction_method = Column(String(50), nullable=False) # STRUCTURED_CDR, NLP_TRIGGER, etc.
    
    # Provenance
    ingestion_job_id = Column(UUID(as_uuid=True), ForeignKey("ingestion_jobs.id"), nullable=False, index=True)
    source_page = Column(Integer, nullable=True)
    source_row = Column(Integer, nullable=True)
    evidence_text = Column(String, nullable=True)
    
    # Context
    event_timestamp = Column(DateTime(timezone=True), nullable=True)

    __table_args__ = (
        # Ensure we don't duplicate the exact same relationship event from the same structured row or page
        UniqueConstraint('source_entity_id', 'target_entity_id', 'relationship_type', 'ingestion_job_id', 'source_page', 'source_row', 'event_timestamp', name='_uniq_relationship_event'),
    )

    # Note: CanonicalEntity relationships would need to be added to CanonicalEntity if bidirectional access is required.
