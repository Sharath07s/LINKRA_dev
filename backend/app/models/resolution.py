import uuid
from sqlalchemy import Column, String, JSON, Text, DateTime
from sqlalchemy import Uuid as UUID
from sqlalchemy.orm import relationship
from app.models.base import BaseModel

class CanonicalEntity(BaseModel):
    """
    A resolved, canonical identity mapped to a Neo4j node.
    Provides a unified identity across multiple EntityCandidate extractions.
    """
    __tablename__ = "canonical_entities"

    entity_type = Column(String(50), nullable=False, index=True) # PERSON, ORGANIZATION, LOCATION, PHONE, VEHICLE, DATE
    name = Column(String(1000), nullable=False)
    
    # Stores other observed names or variations
    aliases = Column(JSON, nullable=True, default=list)
    
    # Normalized extracted metadata, e.g. {"phone": "9876543210"}
    attributes = Column(JSON, nullable=True, default=dict)

    # Relationships
    candidates = relationship("EntityCandidate", back_populates="resolved_to")
