"""
tests/test_rag_ingestion.py
===========================
Verifies the P1 RAG Ingestion pipeline:
Document upload / process_ingestion
  \u2192 parsing
  \u2192 NLP entity extraction & resolution
  \u2192 relationship extraction
  \u2192 structure-aware chunking
  \u2192 pgvector embedding generation
  \u2192 DocumentChunk creation
  \u2192 semantic retrieval via VectorStore.semantic_search()
"""
import os
import uuid
import pytest
from pathlib import Path
from sqlalchemy import select, delete
from unittest.mock import patch

from app.db.session import SessionLocal
from app.models.ingestion import IngestionJob, EntityCandidate
from app.models.relationship import EntityRelationship
from app.models.document import DocumentChunk
from app.ingestion.service import process_ingestion
from app.ai.rag.vector_search import VectorStore

FIXTURES_DIR = Path(__file__).parent / "fixtures" / "ingestion"


def test_rag_ingestion_end_to_end():
    db = SessionLocal()
    test_filename = f"test_fir_{uuid.uuid4().hex[:8]}.txt"
    sample_fir_path = FIXTURES_DIR / "sample_fir.txt"

    assert sample_fir_path.exists(), f"Missing fixture: {sample_fir_path}"

    with open(sample_fir_path, "r", encoding="utf-8") as f:
        file_content = f.read()

    # Create temporary file with unique name so it doesn't collide with existing data
    temp_file_path = FIXTURES_DIR / test_filename
    with open(temp_file_path, "w", encoding="utf-8") as f:
        f.write(file_content)

    job = None
    try:
        # Gracefully mock neo4j sync in case Neo4j is not locally running during test
        with patch("app.nlp.relationship.extractor._sync_to_neo4j", return_value=None), \
             patch("app.nlp.resolution.engine.neo4j_intelligence.sync_canonical_entity", return_value=None):
            job = process_ingestion(
                db=db,
                file_path=str(temp_file_path),
                file_name=test_filename,
                file_type="txt",
                source_type="FIR",
                file_size=len(file_content.encode("utf-8")),
                user_id=None,
            )

        # 1. Assert Job status & counters
        assert job.status == "COMPLETED", f"Job failed with: {job.error_message}"
        assert job.record_count == 1
        assert job.chunk_count is not None
        assert job.chunk_count >= 1, "Expected at least 1 chunk to be indexed into pgvector"

        # 2. Verify DocumentChunk rows in PostgreSQL (pgvector)
        stmt = select(DocumentChunk).where(DocumentChunk.source_id == test_filename)
        chunks = db.execute(stmt).scalars().all()
        assert len(chunks) == job.chunk_count

        for chunk in chunks:
            assert chunk.embedding is not None
            assert len(chunk.embedding) == 384
            assert chunk.metadata_json.get("ingestion_job_id") == str(job.id)
            assert chunk.metadata_json.get("source_filename") == test_filename
            assert chunk.metadata_json.get("source_type") == "FIR"
            assert chunk.metadata_json.get("file_type") == "txt"
            assert chunk.metadata_json.get("page_number") == 1

        # 3. Verify semantic retrieval through VectorStore
        vs = VectorStore()
        search_results = vs.semantic_search("Priya Sharma gold necklace theft", top_k=5)
        assert len(search_results) > 0

        matching = [r for r in search_results if r.get("doc_id") == test_filename]
        assert len(matching) > 0, "Semantic search did not retrieve the indexed test chunk"

        top_match = matching[0]
        assert top_match["similarity"] > 0.3
        assert "Priya Sharma" in top_match["content"]
        assert top_match["metadata"]["source_filename"] == test_filename

        # 4. Phase 2 Verification: EvidenceLink records created
        from app.models.evidence_link import EvidenceLink
        rel_ids = [r.id for r in db.query(EntityRelationship).filter(EntityRelationship.ingestion_job_id == job.id).all()]
        if rel_ids:
            evidence_links = db.query(EvidenceLink).filter(EvidenceLink.relationship_id.in_(rel_ids)).all()
            assert len(evidence_links) > 0, "Expected EvidenceLink records connecting relationships to chunks"
            for link in evidence_links:
                assert link.document_chunk_id in [c.id for c in chunks]
                assert link.quote_snippet is not None

    finally:
        # Cleanup test data
        if temp_file_path.exists():
            temp_file_path.unlink(missing_ok=True)

        if job and job.id:
            from app.models.evidence_link import EvidenceLink
            # Delete evidence links
            rel_subq = select(EntityRelationship.id).where(EntityRelationship.ingestion_job_id == job.id)
            db.execute(delete(EvidenceLink).where(EvidenceLink.relationship_id.in_(rel_subq)))
            # Delete chunks
            db.execute(delete(DocumentChunk).where(DocumentChunk.source_id == test_filename))
            # Delete relationships
            db.execute(delete(EntityRelationship).where(EntityRelationship.ingestion_job_id == job.id))
            # Delete candidates
            db.execute(delete(EntityCandidate).where(EntityCandidate.ingestion_job_id == job.id))
            # Delete job
            db.execute(delete(IngestionJob).where(IngestionJob.id == job.id))
            db.commit()
        db.close()
