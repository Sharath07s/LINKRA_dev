import os
import uuid
from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, select
from langchain_huggingface import HuggingFaceEmbeddings
from app.models.document import DocumentChunk

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
            print(f"Error indexing chunk for job {ingestion_job_id}: {e}")
            return False

    def semantic_search(self, query: str, top_k: int = 5, min_similarity: float = 0.0) -> List[Dict]:
        """
        Converts the query to an embedding and performs a cosine similarity
        search in PGVector. Returns chunks with provenance.
        """
        try:
            query_embedding = self.embedding_model.embed_query(query)
            
            results = []
            with Session(self.engine) as session:
                # Calculate distance using pgvector operator
                distance_col = DocumentChunk.embedding.cosine_distance(query_embedding).label('distance')
                stmt = select(DocumentChunk, distance_col).order_by(distance_col).limit(top_k)
                
                rows = session.execute(stmt).all()
                
                for chunk, distance in rows:
                    similarity = 1.0 - float(distance)
                    
                    if similarity < min_similarity:
                        continue
                        
                    results.append({
                        "chunk_id": str(chunk.id),
                        "ingestion_job_id": str(chunk.ingestion_job_id),
                        "chunk_index": chunk.chunk_index,
                        "page_number": chunk.page_number,
                        "source_row": chunk.source_row,
                        "chunk_text": chunk.chunk_text,
                        "metadata": chunk.metadata_json,
                        "similarity": round(similarity, 4)
                    })
            return results
        except Exception as e:
            print(f"Error in semantic search: {e}")
            return []
