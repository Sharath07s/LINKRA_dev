"""
READ-ONLY database audit script for RAG verification.
Queries only - no writes, no deletes.
"""
import os, sys
sys.path.insert(0, ".")

from app.db.session import SessionLocal
from sqlalchemy import text

db = SessionLocal()
try:
    # 1. DocumentChunk row counts
    dc_total = db.execute(text("SELECT COUNT(*) FROM document_chunks")).scalar()
    dc_with_emb = db.execute(text("SELECT COUNT(*) FROM document_chunks WHERE embedding IS NOT NULL")).scalar()

    # 2. Evidence links
    ev_total = db.execute(text("SELECT COUNT(*) FROM evidence_links")).scalar()

    # 3. Ingestion jobs
    ij_total = db.execute(text("SELECT COUNT(*) FROM ingestion_jobs")).scalar()
    ij_with_chunks = db.execute(text("SELECT COUNT(*) FROM ingestion_jobs WHERE chunk_count IS NOT NULL AND chunk_count > 0")).scalar()
    ij_completed = db.execute(text("SELECT COUNT(*) FROM ingestion_jobs WHERE status='COMPLETED'")).scalar()

    # 4. Entity relationships
    er_total = db.execute(text("SELECT COUNT(*) FROM entity_relationships")).scalar()

    # 5. Check pgvector extension
    try:
        pgv = db.execute(text("SELECT name, default_version, installed_version FROM pg_available_extensions WHERE name='vector'")).fetchone()
        print(f"pgvector extension: {pgv}")
    except Exception as e:
        print(f"pgvector check error: {e}")

    # 6. Check vector column type
    try:
        col_info = db.execute(text("SELECT column_name, udt_name FROM information_schema.columns WHERE table_name='document_chunks' AND column_name='embedding'")).fetchone()
        print(f"embedding column type info: {col_info}")
    except Exception as e:
        print(f"col check error: {e}")

    # 7. Check vector indexes on document_chunks
    try:
        idx_info = db.execute(text("SELECT indexname, indexdef FROM pg_indexes WHERE tablename='document_chunks'")).fetchall()
        print(f"document_chunks indexes: {idx_info}")
    except Exception as e:
        print(f"idx check error: {e}")

    # 8. Sample chunk content if any exist
    if dc_total > 0:
        sample = db.execute(text("SELECT id, source_id, content, metadata_json FROM document_chunks LIMIT 1")).fetchone()
        print(f"Sample chunk id={sample[0]}, source={sample[1]}, content_len={len(sample[2]) if sample[2] else 0}")
        print(f"Sample metadata={sample[3]}")

        # Check embedding dimension of a sample row
        emb_sample = db.execute(text("SELECT array_length(embedding::real[], 1) as dim FROM document_chunks WHERE embedding IS NOT NULL LIMIT 1")).fetchone()
        print(f"Sample embedding dimension: {emb_sample[0] if emb_sample else 'N/A'}")

    print(f"\n--- DATABASE AUDIT RESULTS ---")
    print(f"document_chunks total:               {dc_total}")
    print(f"document_chunks with embeddings:     {dc_with_emb}")
    print(f"evidence_links total:                {ev_total}")
    print(f"ingestion_jobs total:                {ij_total}")
    print(f"ingestion_jobs with chunk_count > 0: {ij_with_chunks}")
    print(f"ingestion_jobs COMPLETED:            {ij_completed}")
    print(f"entity_relationships total:          {er_total}")

finally:
    db.close()
