"""
M15.7.1: Durable Source Recovery Unit Tests

Tests the core behaviors of the durable source storage abstraction and
the updated retry_ingestion_job / restore_source_for_job service functions.

Test categories:
    1.  Storage abstraction: LocalPersistentStorageProvider behaviors
    2.  Storage helpers: make_storage_key, calculate_sha256, sanitize_storage_filename
    3.  Ingestion service: _store_source_durably
    4.  Ingestion service: restore_source_for_job (all branches)
    5.  Ingestion service: retry_ingestion_job ordering (source before cleanup)

All tests use the local storage provider with a temporary directory.
No network/Supabase/PostgreSQL is required (mocked).
"""
import hashlib
import os
import uuid
import tempfile
from pathlib import Path
from datetime import datetime, timezone
from unittest.mock import MagicMock, patch, PropertyMock

import pytest


# ── Helpers ──────────────────────────────────────────────────────────────────

def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


# ── 1. Storage abstraction tests ─────────────────────────────────────────────

class TestLocalPersistentStorageProvider:
    """Tests for LocalPersistentStorageProvider."""

    def _make_provider(self, tmp_path):
        from app.ingestion.storage import LocalPersistentStorageProvider
        return LocalPersistentStorageProvider(root=tmp_path)

    def test_upload_and_download_roundtrip(self, tmp_path):
        provider = self._make_provider(tmp_path)
        data = b"Test FIR document content"
        key = "ingestion/test-job/source/test_fir.txt"

        provider.upload_source(key, data)
        assert provider.source_exists(key)
        downloaded = provider.download_source(key)
        assert downloaded == data

    def test_source_exists_returns_false_for_missing_key(self, tmp_path):
        provider = self._make_provider(tmp_path)
        assert not provider.source_exists("ingestion/nonexistent/source/file.txt")

    def test_download_raises_key_not_found_for_missing_key(self, tmp_path):
        from app.ingestion.storage import StorageKeyNotFoundError
        provider = self._make_provider(tmp_path)
        with pytest.raises(StorageKeyNotFoundError):
            provider.download_source("ingestion/missing/source/file.txt")

    def test_delete_removes_file(self, tmp_path):
        provider = self._make_provider(tmp_path)
        data = b"Will be deleted"
        key = "ingestion/test-job/source/delete_me.txt"
        provider.upload_source(key, data)
        assert provider.source_exists(key)
        provider.delete_source(key)
        assert not provider.source_exists(key)

    def test_path_traversal_is_blocked(self, tmp_path):
        from app.ingestion.storage import StoragePermissionError
        provider = self._make_provider(tmp_path)
        malicious_key = "../../etc/passwd"
        with pytest.raises(StoragePermissionError):
            provider.upload_source(malicious_key, b"evil")

    def test_upload_overwrites_existing(self, tmp_path):
        provider = self._make_provider(tmp_path)
        key = "ingestion/test-job/source/file.txt"
        provider.upload_source(key, b"original")
        provider.upload_source(key, b"updated")
        assert provider.download_source(key) == b"updated"

    def test_get_source_metadata_returns_size(self, tmp_path):
        provider = self._make_provider(tmp_path)
        data = b"Metadata test content"
        key = "ingestion/test-job/source/meta.txt"
        provider.upload_source(key, data)
        meta = provider.get_source_metadata(key)
        assert meta is not None
        assert meta["size"] == len(data)

    def test_get_source_metadata_returns_none_for_missing(self, tmp_path):
        provider = self._make_provider(tmp_path)
        assert provider.get_source_metadata("ingestion/nope/source/x.txt") is None


# ── 2. Storage helpers tests ─────────────────────────────────────────────────

class TestStorageHelpers:
    def test_make_storage_key_format(self):
        from app.ingestion.storage import make_storage_key
        job_id = "3fa85f64-5717-4562-b3fc-2c963f66afa6"
        key = make_storage_key(job_id, "test_fir.pdf")
        assert key == f"ingestion/{job_id}/source/test_fir.pdf"

    def test_make_storage_key_sanitizes_filename(self):
        from app.ingestion.storage import make_storage_key
        key = make_storage_key("abc", "../../../etc/passwd")
        # Traversal component stripped, only basename kept
        assert ".." not in key
        assert "etc" not in key.split("source/")[-1] or "passwd" in key

    def test_calculate_sha256_consistency(self):
        from app.ingestion.storage import calculate_sha256
        data = b"LINKRA ingestion test"
        assert calculate_sha256(data) == _sha256(data)

    def test_calculate_sha256_empty(self):
        from app.ingestion.storage import calculate_sha256
        assert calculate_sha256(b"") == _sha256(b"")

    def test_sanitize_strips_path_traversal(self):
        from app.ingestion.storage import sanitize_storage_filename
        assert ".." not in sanitize_storage_filename("../../malicious.txt")

    def test_sanitize_handles_unicode(self):
        from app.ingestion.storage import sanitize_storage_filename
        result = sanitize_storage_filename("FIR_काण्ड_01.pdf")
        assert result  # Not empty
        assert len(result) <= 200


# ── 3. _store_source_durably tests ───────────────────────────────────────────

class TestStoreSourcDurably:
    def _make_job(self):
        job = MagicMock()
        job.id = uuid.uuid4()
        job.source_storage_provider = None
        job.source_storage_key = None
        job.source_original_filename = None
        job.source_content_type = None
        job.source_size_bytes = None
        job.source_sha256 = None
        job.source_storage_bucket = None
        job.source_uploaded_at = None
        return job

    def test_stores_bytes_and_sets_metadata(self, tmp_path):
        from app.ingestion.storage import reset_storage_provider, LocalPersistentStorageProvider
        import app.ingestion.storage as storage_module
        reset_storage_provider()

        with patch.dict(os.environ, {"SOURCE_STORAGE_PROVIDER": "local"}):
            with patch.object(storage_module, "STORAGE_ROOT", tmp_path):
                reset_source_provider = storage_module.reset_storage_provider
                reset_source_provider()

                db = MagicMock()
                job = self._make_job()
                data = b"FIR document"

                from app.ingestion.service import _store_source_durably
                _store_source_durably(db, job, data, "fir.txt", "text/plain")

                # Metadata fields should be set
                assert job.source_storage_key is not None
                assert job.source_sha256 == _sha256(data)
                assert job.source_size_bytes == len(data)
                db.commit.assert_called()

    def test_does_not_raise_on_storage_failure(self, tmp_path):
        """If storage upload fails, _store_source_durably should warn but not raise."""
        from app.ingestion.storage import StorageUploadError
        from app.ingestion.service import _store_source_durably

        db = MagicMock()
        job = self._make_job()

        with patch("app.ingestion.service.get_storage_provider") as mock_provider:
            mock_instance = MagicMock()
            mock_instance.upload_source.side_effect = StorageUploadError("disk full")
            mock_provider.return_value = mock_instance

            # Should not raise
            _store_source_durably(db, job, b"data", "file.txt", "text/plain")


# ── 4. restore_source_for_job tests ──────────────────────────────────────────

class TestRestoreSourceForJob:
    def _make_job(self, storage_key=None, sha256=None, file_name="test.txt"):
        job = MagicMock()
        job.id = uuid.uuid4()
        job.file_name = file_name
        job.source_storage_key = storage_key
        job.source_sha256 = sha256
        job.source_original_filename = file_name
        return job

    def test_returns_local_path_when_file_exists(self, tmp_path):
        """If the local file exists and checksum matches, returns its path."""
        from app.ingestion.service import UPLOAD_DIR, restore_source_for_job
        data = b"local content"
        job = self._make_job(storage_key="some/key", sha256=_sha256(data), file_name="localfile.txt")

        local_file = UPLOAD_DIR / f"aabbcc_{job.file_name}"
        local_file.write_bytes(data)

        db = MagicMock()
        try:
            result = restore_source_for_job(db, job)
            assert str(local_file) == result
        finally:
            local_file.unlink(missing_ok=True)

    def test_raises_permanent_failure_when_no_durable_key(self):
        """If local file missing AND no durable storage key, raises permanent failure."""
        from app.ingestion.storage import StorageKeyNotFoundError
        from app.ingestion.service import restore_source_for_job

        job = self._make_job(storage_key=None, sha256=None, file_name="definitely_missing_xyz123.txt")
        db = MagicMock()

        with pytest.raises(StorageKeyNotFoundError):
            restore_source_for_job(db, job)

        # Job must be marked PERMANENT_FAILURE
        assert job.status == "FAILED"
        assert job.error_code == "SOURCE_FILE_MISSING"
        assert job.recovery_status == "PERMANENT_FAILURE"

    def test_raises_permanent_failure_when_durable_key_missing_in_storage(self):
        """If durable key set but not found in storage, raises permanent failure."""
        from app.ingestion.storage import StorageKeyNotFoundError
        from app.ingestion.service import restore_source_for_job

        job = self._make_job(
            storage_key="ingestion/job123/source/missing.txt",
            sha256=_sha256(b"some"),
            file_name="missing_abc999.txt",
        )
        db = MagicMock()

        with patch("app.ingestion.service.get_storage_provider") as mock_prov:
            mock_storage = MagicMock()
            mock_storage.source_exists.return_value = False
            mock_prov.return_value = mock_storage

            with pytest.raises(StorageKeyNotFoundError):
                restore_source_for_job(db, job)

        assert job.error_code == "SOURCE_FILE_MISSING"
        assert job.recovery_status == "PERMANENT_FAILURE"

    def test_raises_permanent_failure_on_checksum_mismatch(self, tmp_path):
        """If restored bytes have wrong SHA-256, raises permanent failure."""
        from app.ingestion.service import restore_source_for_job

        original_data = b"original content"
        corrupted_data = b"corrupted content"

        job = self._make_job(
            storage_key="ingestion/job/source/file.txt",
            sha256=_sha256(original_data),  # checksum of original
            file_name="checksum_test_xyz789.txt",
        )
        db = MagicMock()

        with patch("app.ingestion.service.get_storage_provider") as mock_prov:
            mock_storage = MagicMock()
            mock_storage.source_exists.return_value = True
            mock_storage.download_source.return_value = corrupted_data  # Wrong bytes!
            mock_prov.return_value = mock_storage

            with pytest.raises(ValueError, match="SHA-256"):
                restore_source_for_job(db, job)

        assert job.error_code == "SOURCE_FILE_INTEGRITY_MISMATCH"
        assert job.recovery_status == "PERMANENT_FAILURE"

    def test_restores_and_returns_local_path_on_success(self, tmp_path):
        """If durable source exists and SHA-256 matches, restores and returns path."""
        from app.ingestion.service import restore_source_for_job, UPLOAD_DIR

        data = b"Recoverable FIR content"
        sha = _sha256(data)

        job = self._make_job(
            storage_key="ingestion/job/source/recoverable.txt",
            sha256=sha,
            file_name="recoverable_xyz000.txt",
        )
        db = MagicMock()

        with patch("app.ingestion.service.get_storage_provider") as mock_prov:
            mock_storage = MagicMock()
            mock_storage.source_exists.return_value = True
            mock_storage.download_source.return_value = data
            mock_prov.return_value = mock_storage

            restored_path = restore_source_for_job(db, job)

        assert os.path.exists(restored_path)
        assert Path(restored_path).read_bytes() == data

        # Cleanup
        Path(restored_path).unlink(missing_ok=True)


# ── 5. retry_ingestion_job ordering test ─────────────────────────────────────

class TestRetryJobOrdering:
    """
    Verify that the M15.7.1 critical ordering is enforced:
    source restoration happens BEFORE cleanup_job_outputs.
    """

    def test_cleanup_not_called_when_source_missing(self):
        """If source restoration fails, cleanup_job_outputs must NOT be called."""
        from app.ingestion.storage import StorageKeyNotFoundError
        import app.ingestion.service as svc

        job = MagicMock()
        job.id = uuid.uuid4()
        job.status = "FAILED"
        job.retry_count = 0
        job.max_retry_count = 3
        job.recovery_status = "RETRYABLE"
        job.is_deleted = False

        db = MagicMock()
        db.query.return_value.filter.return_value.first.return_value = job

        cleanup_called = []

        def mock_cleanup(db_arg, job_id):
            cleanup_called.append(True)

        def mock_restore_fail(db_arg, job_arg):
            job.status = "FAILED"
            job.error_code = "SOURCE_FILE_MISSING"
            job.recovery_status = "PERMANENT_FAILURE"
            raise StorageKeyNotFoundError("No durable source")

        with patch.object(svc, "cleanup_job_outputs", side_effect=mock_cleanup):
            with patch.object(svc, "restore_source_for_job", side_effect=mock_restore_fail):
                with pytest.raises(FileNotFoundError):
                    svc.retry_ingestion_job(db, job.id)

        assert len(cleanup_called) == 0, (
            "cleanup_job_outputs was called BEFORE source verification succeeded — critical ordering bug!"
        )

    def test_cleanup_called_only_after_successful_restore(self):
        """If restoration succeeds, cleanup_job_outputs IS called, then pipeline runs."""
        import app.ingestion.service as svc

        job = MagicMock()
        job.id = uuid.uuid4()
        job.status = "FAILED"
        job.retry_count = 0
        job.max_retry_count = 3
        job.recovery_status = "RETRYABLE"
        job.is_deleted = False

        db = MagicMock()
        db.query.return_value.filter.return_value.first.return_value = job

        call_order = []

        def mock_restore_ok(db_arg, job_arg):
            call_order.append("restore")
            return "/tmp/fake_source.txt"

        def mock_cleanup(db_arg, job_id):
            call_order.append("cleanup")

        def mock_pipeline(db_arg, job_arg, file_path):
            call_order.append("pipeline")
            return job

        with patch.object(svc, "restore_source_for_job", side_effect=mock_restore_ok):
            with patch.object(svc, "cleanup_job_outputs", side_effect=mock_cleanup):
                with patch.object(svc, "execute_pipeline", side_effect=mock_pipeline):
                    svc.retry_ingestion_job(db, job.id)

        assert call_order == ["restore", "cleanup", "pipeline"], (
            f"Incorrect execution order: {call_order}. "
            "Expected: restore → cleanup → pipeline"
        )
