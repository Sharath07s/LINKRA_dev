import os
import logging
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
        """
        if not connection_string:
            from app.core.config import settings
            self.connection_string = settings.SQLALCHEMY_DATABASE_URI
        else:
            self.connection_string = connection_string
            
        self.engine = create_engine(self.connection_string)
        self.embedding_model = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

    def index_document(self, source_id: str, text: str, metadata: dict) -> bool:
        """
        Embeds the text and inserts the embedding into PGVector.
        """
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
                    source_id=source_id,
                    content=text,
                    metadata_json=metadata,
                    embedding=embedding
                )
                session.add(chunk)
                session.commit()
            return True
        except Exception as e:
            logger.error(f"Error indexing document {source_id}: {e}", exc_info=True)
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
                        "doc_id": chunk.source_id,
                        "content": chunk.content,
                        "metadata": chunk.metadata_json,
                        "similarity": round(similarity, 4)
                    })
            return results
        except Exception as e:
            logger.error(f"Error in semantic search: {e}", exc_info=True)
            return []
