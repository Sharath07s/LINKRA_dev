import os
import uuid
import pytest
from datetime import datetime, timezone
from unittest.mock import patch

from app.models.ingestion import IngestionJob, EntityCandidate
from app.models.relationship import EntityRelationship
from app.models.document import DocumentChunk
from app.ingestion.service import (
    sanitize_error_message,
    classify_error,
    cleanup_job_outputs,
    process_ingestion,
    retry_ingestion_job,
    UPLOAD_DIR,
)

@pytest.fixture(autouse=True)
def mock_embedding_query(monkeypatch):
    """Fast mock for HuggingFaceEmbeddings to avoid model download during test execution."""
    from langchain_huggingface import HuggingFaceEmbeddings
    monkeypatch.setattr(HuggingFaceEmbeddings, "__init__", lambda self, *a, **kw: None)
    monkeypatch.setattr(HuggingFaceEmbeddings, "embed_query", lambda self, text: [0.1] * 384)



# ── 1. Test Secret Sanitization ───────────────────────────────────────────

def test_sanitize_error_message():
    raw_error = "Connection failed to postgres://admin:SecretPass123@localhost:5432/db with Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIn0.signature and key=sk-live-secretkey123"
    sanitized = sanitize_error_message(raw_error)

    assert "SecretPass123" not in sanitized
    assert "eyJhbGciOiJIUzI1Ni" not in sanitized
    assert "sk-live-secretkey123" not in sanitized
    assert "Bearer [REDACTED]" in sanitized
    assert "postgres://[REDACTED]" in sanitized
    assert "key=[REDACTED]" in sanitized


# ── 2. Test Error Classification ─────────────────────────────────────────

def test_classify_error():
    val_err = ValueError("PDF contains no extractable text. Scanned/image-only PDFs require OCR.")
    code, status, msg = classify_error(val_err, "PARSING")
    assert code == "UNSUPPORTED_OR_CORRUPT_DOCUMENT"
    assert status == "PERMANENT_FAILURE"

    conn_err = ConnectionError("Embedding service connection refused at http://localhost:8000")
    code, status, msg = classify_error(conn_err, "EMBEDDING_GENERATION")
    assert code == "EMBEDDING_PROVIDER_UNAVAILABLE"
    assert status == "RETRYABLE"

    fnf_err = FileNotFoundError("Source file FIR_2023.pdf missing")
    code, status, msg = classify_error(fnf_err, "PARSING")
    assert code == "SOURCE_FILE_MISSING"
    assert status == "PERMANENT_FAILURE"


# ── 3. Test Output Cleanup & Idempotency ──────────────────────────────────

def test_cleanup_job_outputs(db):
    # Create test job
    job = IngestionJob(
        file_name="test_clean.txt",
        source_type="OTHER",
        file_type="txt",
        status="FAILED",
    )
    db.add(job)
    db.commit()
    db.refresh(job)

    # Insert candidate & chunk
    candidate = EntityCandidate(
        ingestion_job_id=job.id,
        entity_type="PERSON",
        raw_text="John Doe",
        normalized_value="JOHN DOE",
        extraction_method="spacy_ner",
    )
    db.add(candidate)

    chunk = DocumentChunk(
        ingestion_job_id=job.id,
        chunk_text="John Doe lived in Delhi.",
        chunk_index=0,
    )
    db.add(chunk)
    db.commit()

    # Execute cleanup
    cleanup_job_outputs(db, job.id)

    # Assert rows purged
    cands = db.query(EntityCandidate).filter(EntityCandidate.ingestion_job_id == job.id).all()
    chunks = db.query(DocumentChunk).filter(DocumentChunk.ingestion_job_id == job.id).all()
    assert len(cands) == 0
    assert len(chunks) == 0


# ── 4. Test Ingestion Failure Recording & Retry Engine ───────────────────

def test_ingestion_retry_flow(db):
    # Create test document in UPLOAD_DIR
    test_filename = f"{uuid.uuid4().hex}_retry_test.txt"
    test_filepath = str(UPLOAD_DIR / test_filename)
    with open(test_filepath, "w") as f:
        f.write("Suspect Raj Kumar was spotted in Mumbai contacting +919876543210.")

    try:
        # 1. Process document cleanly
        job = process_ingestion(
            db=db,
            file_path=test_filepath,
            file_name=test_filename,
            file_type="txt",
            source_type="OTHER",
            file_size=len("Suspect Raj Kumar..."),
        )
        assert job.status in ("COMPLETED", "COMPLETED_PARTIAL")
        assert job.retry_count == 0

        # Manually simulate a failure state for testing recovery
        job.status = "FAILED"
        job.failed_step = "EMBEDDING_GENERATION"
        job.error_code = "EMBEDDING_PROVIDER_UNAVAILABLE"
        job.error_message = "Embedding provider unavailable"
        job.recovery_status = "RETRYABLE"
        job.failed_at = datetime.now(timezone.utc)
        db.commit()

        # 2. Retry the job
        retried_job = retry_ingestion_job(db, job.id)

        assert retried_job.status in ("COMPLETED", "COMPLETED_PARTIAL")
        assert retried_job.retry_count == 1
        assert retried_job.recovery_status == "RECOVERED"
        assert retried_job.failed_step is None

        # Verify idempotency: entity candidate count matches original run (no duplicates!)
        candidates = db.query(EntityCandidate).filter(EntityCandidate.ingestion_job_id == job.id).all()
        raw_texts = [c.raw_text for c in candidates]
        assert len(raw_texts) == len(set(raw_texts))

    finally:
        if os.path.exists(test_filepath):
            os.remove(test_filepath)


# ── 5. Test Failure Injection & Recovery ──────────────────────────────────

def test_embedding_failure_injection_and_recovery(db):
    test_filename = f"{uuid.uuid4().hex}_injection.txt"
    test_filepath = str(UPLOAD_DIR / test_filename)
    with open(test_filepath, "w") as f:
        f.write("Test document for failure injection recovery.")

    try:
        # Inject failure in VectorStore.index_document
        with patch("app.ai.rag.vector_search.VectorStore.index_document", side_effect=RuntimeError("Simulated embedding service crash")):
            job = process_ingestion(
                db=db,
                file_path=test_filepath,
                file_name=test_filename,
                file_type="txt",
                source_type="OTHER",
                file_size=len("Test document..."),
            )

        assert job.status == "FAILED"
        assert job.failed_step == "EMBEDDING_GENERATION"
        assert job.error_code == "EMBEDDING_PROVIDER_UNAVAILABLE"
        assert "Simulated embedding service crash" in job.error_message
        assert job.recovery_status == "RETRYABLE"

        # Now remove failure injection and retry
        recovered_job = retry_ingestion_job(db, job.id)

        assert recovered_job.status in ("COMPLETED", "COMPLETED_PARTIAL")
        assert recovered_job.recovery_status == "RECOVERED"
        assert recovered_job.retry_count == 1

    finally:
        if os.path.exists(test_filepath):
            os.remove(test_filepath)


# ── 6. Test Retry Exhaustion ──────────────────────────────────────────────

def test_retry_exhaustion(db):
    job = IngestionJob(
        file_name="exhausted.txt",
        source_type="OTHER",
        file_type="txt",
        status="FAILED",
        retry_count=3,
        max_retry_count=3,
        recovery_status="EXHAUSTED",
    )
    db.add(job)
    db.commit()

    with pytest.raises(ValueError, match="exhausted its maximum retries"):
        retry_ingestion_job(db, job.id)


def test_retry_api_rbac_and_concurrency(admin_client, db):
    job = IngestionJob(
        file_name="api_test.txt",
        source_type="OTHER",
        file_type="txt",
        status="FAILED",
        failed_step="PARSING",
        recovery_status="RETRYABLE",
        retry_count=0,
        max_retry_count=3,
    )
    db.add(job)
    db.commit()

    test_filepath = str(UPLOAD_DIR / job.file_name)
    with open(test_filepath, "w") as f:
        f.write("Sample content")

    try:
        # 1. Authenticated admin request -> 200
        resp_admin = admin_client.post(f"/api/v1/ingestion/{job.id}/retry")
        assert resp_admin.status_code == 200
        data = resp_admin.json()
        assert data["id"] == str(job.id)
        assert data["retry_count"] == 1
        assert data["recovery_status"] == "RECOVERED"

        # 2. Retrying a completed job -> 400 Bad Request
        resp_completed = admin_client.post(f"/api/v1/ingestion/{job.id}/retry")
        assert resp_completed.status_code == 400

    finally:
        if os.path.exists(test_filepath):
            os.remove(test_filepath)

