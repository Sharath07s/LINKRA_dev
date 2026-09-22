import os
import logging
import uuid
from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, select
from langchain_huggingface import HuggingFaceEmbeddings
from app.models.document import DocumentChunk

logger = logging.getLogger(__name__)

class VectorStore:
    def __init__(self, connection_string: str = None):
        """
        Initializes the VectorStore, natively integrating with PGVector.
        Embedding model configured via EMBEDDING_MODEL_NAME env var, falls back to all-MiniLM-L6-v2.
        """
        if not connection_string:
            from app.core.config import settings
            self.connection_string = settings.SQLALCHEMY_DATABASE_URI
        else:
            self.connection_string = connection_string
            
        self.engine = create_engine(self.connection_string)
        model_name = os.environ.get("EMBEDDING_MODEL_NAME", "all-MiniLM-L6-v2")
        self.embedding_model = HuggingFaceEmbeddings(model_name=model_name)

    def index_document(self, 
                       ingestion_job_id: uuid.UUID, 
                       text: str, 
                       chunk_index: int = 0,
                       page_number: Optional[int] = None,
                       source_row: Optional[int] = None,
                       metadata: dict = None) -> bool:
        """
        Embeds the text and inserts the embedding into PGVector with proper provenance.
        """
        if metadata is None:
            metadata = {}
            
        try:
            embedding = self.embedding_model.embed_query(text)
            if not embedding or len(embedding) != 384:
                logger.error(
                    f"Invalid embedding for {source_id}: "
                    f"expected 384 dimensions, got {len(embedding) if embedding else None}"
                )
                return False
            
            with Session(self.engine) as session:
                chunk = DocumentChunk(
                    ingestion_job_id=ingestion_job_id,
                    chunk_text=text,
                    chunk_index=chunk_index,
                    page_number=page_number,
                    source_row=source_row,
                    metadata_json=metadata,
                    embedding=embedding
                )
                session.add(chunk)
                session.commit()
            return True
        except Exception as e:
            logger.error(f"Error indexing chunk for job {ingestion_job_id}: {e}", exc_info=True)
            return False

    def semantic_search(
        self,
        query: str,
        top_k: int = 5,
        source_id: Optional[str] = None,
        ingestion_job_id: Optional[str] = None,
        min_similarity: Optional[float] = None,
    ) -> List[Dict]:
        """
        Converts the query to an embedding and performs a cosine similarity
        search in PGVector with optional metadata and threshold filtering.
        """
        try:
            query_embedding = self.embedding_model.embed_query(query)
            
            results = []
            with Session(self.engine) as session:
                # Calculate distance using pgvector operator
                distance_col = DocumentChunk.embedding.cosine_distance(query_embedding).label('distance')
                stmt = (
                    select(DocumentChunk, distance_col)
                    .where(DocumentChunk.embedding.isnot(None))
                )
                
                if source_id:
                    stmt = stmt.where(DocumentChunk.source_id == source_id)
                if ingestion_job_id:
                    stmt = stmt.where(
                        DocumentChunk.metadata_json["ingestion_job_id"].as_string() == str(ingestion_job_id)
                    )
                
                stmt = stmt.order_by(distance_col).limit(top_k)
                
                rows = session.execute(stmt).all()
                
                for chunk, distance in rows:
                    if distance is None:
                        continue
                    similarity = 1.0 - float(distance)
                    if min_similarity is not None and similarity < min_similarity:
                        continue
                        
                    results.append({
                        "chunk_id": str(chunk.id),
                        "ingestion_job_id": str(chunk.ingestion_job_id) if hasattr(chunk, 'ingestion_job_id') else None,
                        "chunk_index": getattr(chunk, 'chunk_index', None),
                        "page_number": getattr(chunk, 'page_number', None),
                        "source_row": getattr(chunk, 'source_row', None),
                        "chunk_text": chunk.chunk_text,
                        "metadata": chunk.metadata_json,
                        "similarity": round(similarity, 4)
                    })
            return results
        except Exception as e:
            logger.error(f"Error in semantic search: {e}", exc_info=True)
            return []
