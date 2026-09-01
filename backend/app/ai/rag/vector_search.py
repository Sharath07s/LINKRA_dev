import os
from typing import List, Dict
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, select
from langchain_huggingface import HuggingFaceEmbeddings
from app.models.document import DocumentChunk

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
            print(f"Error indexing document {source_id}: {e}")
            return False

    def semantic_search(self, query: str, top_k: int = 5) -> List[Dict]:
        """
        Converts the query to an embedding and performs a cosine similarity
        search in PGVector.
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
                    results.append({
                        "doc_id": chunk.source_id,
                        "content": chunk.content,
                        "metadata": chunk.metadata_json,
                        "similarity": round(similarity, 4)
                    })
            return results
        except Exception as e:
            print(f"Error in semantic search: {e}")
            return []
