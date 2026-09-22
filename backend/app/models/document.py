from sqlalchemy import Column, String, Integer, Text, DateTime, JSON, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy import Uuid as UUID
from pgvector.sqlalchemy import Vector
from app.models.base import BaseModel
from datetime import datetime


class DocumentChunk(BaseModel):
    """
    A chunk of actual source document text with its vector embedding.
    
    Provenance chain:
        IngestionJob (file) → DocumentChunk (text segment) → Embedding (vector)
    
    Used by the RAG pipeline to ground Copilot answers in real document evidence.
    """
    __tablename__ = "document_chunks"

    # Link back to the ingestion job that produced this chunk
    ingestion_job_id = Column(UUID(as_uuid=True), ForeignKey("ingestion_jobs.id"), nullable=False, index=True)

    # Chunk ordering and content
    chunk_index = Column(Integer, nullable=False, default=0)
    chunk_text = Column(Text, nullable=False)

    # Source provenance
    page_number = Column(Integer, nullable=True)   # For PDFs / TXT
    source_row = Column(Integer, nullable=True)     # For CSV / JSON

    # Extensible metadata (e.g. original filename, parser version)
    metadata_json = Column(JSON, default={})

    # 384 dimensions for all-MiniLM-L6-v2 model
    embedding = Column(Vector(384))

    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    ingestion_job = relationship("IngestionJob")
