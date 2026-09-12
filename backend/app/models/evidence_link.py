"""
backend/app/models/evidence_link.py
===================================
Represents an evidence association connecting knowledge graph elements
(EntityRelationship or EntityCandidate) to their supporting RAG DocumentChunk.
"""
from sqlalchemy import Column, String, Integer, Float, Text, ForeignKey
from sqlalchemy import Uuid as UUID
from sqlalchemy.orm import relationship
from app.models.base import BaseModel


class EvidenceLink(BaseModel):
    """
    Grounds extracted graph intelligence into specific DocumentChunk rows.
    """
    __tablename__ = "evidence_links"

    relationship_id = Column(
        UUID(as_uuid=True),
        ForeignKey("entity_relationships.id", ondelete="CASCADE"),
        nullable=True,
        index=True
    )
    candidate_id = Column(
        UUID(as_uuid=True),
        ForeignKey("entity_candidates.id", ondelete="CASCADE"),
        nullable=True,
        index=True
    )
    document_chunk_id = Column(
        UUID(as_uuid=True),
        ForeignKey("document_chunks.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    char_start = Column(Integer, nullable=True)
    char_end = Column(Integer, nullable=True)
    quote_snippet = Column(Text, nullable=False)
    confidence = Column(Float, nullable=False, default=1.0)

    # Relationships
    entity_relationship = relationship("EntityRelationship", backref="evidence_links")
    entity_candidate = relationship("EntityCandidate", backref="evidence_links")
    document_chunk = relationship("DocumentChunk", backref="evidence_links")
