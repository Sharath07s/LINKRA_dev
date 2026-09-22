"""
Durable Source Storage Abstraction — M15.7.1

Provides a provider-agnostic interface for storing, verifying, and restoring
original ingestion source files.

Architecture:
    IngestionService
          ↓
    SourceStorage (this module)
          ↓
    Provider (LocalPersistentStorageProvider | SupabaseStorageProvider)

Provider Selection (via env var SOURCE_STORAGE_PROVIDER):
    'local'    → LocalPersistentStorageProvider  (default, for dev/test)
    'supabase' → SupabaseStorageProvider          (requires SUPABASE_URL + creds)

Security:
    - Filenames are sanitized to prevent path traversal
    - Storage keys use job_id as namespace
    - Credentials are NEVER logged or stored in PostgreSQL
    - SupabaseStorageProvider uses server-side service-role key only
"""
import hashlib
import logging
import os
import re
import shutil
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

# ── Constants ────────────────────────────────────────────────────────────────

STORAGE_ROOT = Path(__file__).resolve().parent.parent.parent.parent / "storage" / "ingestion"
"""Persistent local storage root. Survives process restarts (unlike /tmp)."""


# ── Exceptions ───────────────────────────────────────────────────────────────

class StorageUnavailableError(Exception):
    """Raised when the storage backend is temporarily unreachable."""


class StoragePermissionError(Exception):
    """Raised when authentication/authorization to the storage backend fails."""


class StorageDownloadError(Exception):
    """Raised when a download from storage fails (network, partial response, etc.)."""


class StorageUploadError(Exception):
    """Raised when an upload to storage fails."""


class StorageKeyNotFoundError(Exception):
    """Raised when the requested storage key does not exist."""


# ── Helpers ──────────────────────────────────────────────────────────────────

def sanitize_storage_filename(filename: str) -> str:
    """
    Sanitize a user-provided filename so it is safe for use in storage keys.

    - Strips leading/trailing whitespace
    - Replaces any path separators or unusual characters with underscores
    - Limits length to 200 characters
    - Prevents path traversal (../, .\\, absolute paths)
    """
    if not filename:
        return "unknown_file"

    # Take only the basename (strip any directory components)
    safe = Path(filename).name

    # Replace path-separator-like characters and whitespace with underscores
    safe = re.sub(r"[/\\:\s]+", "_", safe)

    # Keep only alphanumeric, underscore, hyphen, dot
    safe = re.sub(r"[^\w\-.]", "_", safe)

    # Prevent double dots (path traversal attempt)
    safe = re.sub(r"\.{2,}", "_", safe)

    # Limit length
    if len(safe) > 200:
        ext = Path(safe).suffix
        stem = Path(safe).stem[:200 - len(ext)]
        safe = stem + ext

    return safe or "unknown_file"


def make_storage_key(job_id: str, original_filename: str) -> str:
    """
    Build a deterministic, namespaced storage key for a source file.

    Format: ingestion/{job_id}/source/{sanitized_filename}

    Example:
        ingestion/3fa85f64-5717-4562-b3fc-2c963f66afa6/source/fir_report.pdf
    """
    safe_name = sanitize_storage_filename(original_filename)
    return f"ingestion/{job_id}/source/{safe_name}"


def calculate_sha256(data: bytes) -> str:
    """Calculate the SHA-256 checksum of raw bytes."""
    return hashlib.sha256(data).hexdigest()


# ── Abstract Interface ────────────────────────────────────────────────────────

class SourceStorage(ABC):
    """
    Abstract interface for durable source file storage.

    All implementations must be safe to call concurrently and must not
    leak credentials in exceptions or log output.
    """

    @abstractmethod
    def upload_source(self, storage_key: str, data: bytes, content_type: str = "application/octet-stream") -> None:
        """
        Upload raw file bytes under the given storage_key.

        Raises:
            StorageUploadError:     On upload failure
            StorageUnavailableError: If the backend is temporarily down
            StoragePermissionError: On auth failure
        """

    @abstractmethod
    def source_exists(self, storage_key: str) -> bool:
        """
        Check whether the given storage_key exists in storage.

        Returns False if not found.
        Raises StorageUnavailableError if the check itself cannot be performed.
        Raises StoragePermissionError on auth failure.
        """

    @abstractmethod
    def get_source_metadata(self, storage_key: str) -> Optional[dict]:
        """
        Return metadata for the storage object (size, content_type, etc.)
        or None if the key does not exist.
        """

    @abstractmethod
    def download_source(self, storage_key: str) -> bytes:
        """
        Download and return the raw bytes for the given storage_key.

        Raises:
            StorageKeyNotFoundError: If the key does not exist
            StorageDownloadError:    On download failure
            StorageUnavailableError: If the backend is temporarily down
            StoragePermissionError:  On auth failure
        """

    @abstractmethod
    def delete_source(self, storage_key: str) -> None:
        """
        Delete the object at storage_key (used only if retention policy allows).

        Raises:
            StorageUnavailableError: If the backend is temporarily down
            StoragePermissionError:  On auth failure
        """


# ── Local Persistent Provider ────────────────────────────────────────────────

class LocalPersistentStorageProvider(SourceStorage):
    """
    Persistent local filesystem storage provider.

    Stores objects under: storage/ingestion/{key}

    This directory survives process restarts (unlike /tmp).
    Suitable for development, testing, and single-server deployments.

    NOT suitable for multi-server or containerized environments
    where the filesystem is ephemeral or not shared.
    """

    def __init__(self, root: Optional[Path] = None):
        self.root = root or STORAGE_ROOT
        self.root.mkdir(parents=True, exist_ok=True)
        logger.info(f"[LocalStorage] Storage root: {self.root}")

    def _path_for(self, storage_key: str) -> Path:
        """Resolve storage_key to an absolute filesystem path safely."""
        # Prevent path traversal: normalize and verify it stays within root
        resolved = (self.root / storage_key).resolve()
        if not str(resolved).startswith(str(self.root.resolve())):
            raise StoragePermissionError(f"Path traversal detected in storage key: [REDACTED]")
        return resolved

    def upload_source(self, storage_key: str, data: bytes, content_type: str = "application/octet-stream") -> None:
        try:
            dest = self._path_for(storage_key)
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(data)
            logger.info(f"[LocalStorage] SOURCE_DURABLE_UPLOAD_SUCCESS key={storage_key} size={len(data)}")
        except StoragePermissionError:
            raise
        except Exception as e:
            logger.error(f"[LocalStorage] SOURCE_DURABLE_UPLOAD_FAILED key={storage_key} error={type(e).__name__}")
            raise StorageUploadError(f"Failed to write to local storage: {type(e).__name__}") from e

    def source_exists(self, storage_key: str) -> bool:
        try:
            return self._path_for(storage_key).exists()
        except StoragePermissionError:
            raise
        except Exception as e:
            raise StorageUnavailableError(f"Cannot check local storage: {type(e).__name__}") from e

    def get_source_metadata(self, storage_key: str) -> Optional[dict]:
        try:
            p = self._path_for(storage_key)
            if not p.exists():
                return None
            stat = p.stat()
            return {"size": stat.st_size, "content_type": "application/octet-stream"}
        except StoragePermissionError:
            raise
        except Exception:
            return None

    def download_source(self, storage_key: str) -> bytes:
        try:
            p = self._path_for(storage_key)
            if not p.exists():
                raise StorageKeyNotFoundError(f"Storage key not found in local storage")
            data = p.read_bytes()
            logger.info(f"[LocalStorage] SOURCE_RESTORE_SUCCESS key={storage_key} size={len(data)}")
            return data
        except (StorageKeyNotFoundError, StoragePermissionError):
            raise
        except Exception as e:
            logger.error(f"[LocalStorage] SOURCE_RESTORE_FAILED key={storage_key} error={type(e).__name__}")
            raise StorageDownloadError(f"Failed to read from local storage: {type(e).__name__}") from e

    def delete_source(self, storage_key: str) -> None:
        try:
            p = self._path_for(storage_key)
            if p.exists():
                p.unlink()
                logger.info(f"[LocalStorage] Deleted storage key={storage_key}")
        except StoragePermissionError:
            raise
        except Exception as e:
            raise StorageUnavailableError(f"Cannot delete from local storage: {type(e).__name__}") from e


# ── Supabase Storage Provider ────────────────────────────────────────────────

class SupabaseStorageProvider(SourceStorage):
    """
    Supabase Storage provider.

    Requires:
        SUPABASE_URL             — e.g. https://<project>.supabase.co
        SUPABASE_SERVICE_ROLE_KEY — server-side secret, never exposed to frontend
        SOURCE_STORAGE_BUCKET    — the storage bucket name

    Credentials are loaded from environment variables ONLY.
    They are NEVER logged, stored in PostgreSQL, or exposed in error messages.
    """

    def __init__(self):
        self.url = os.environ.get("SUPABASE_URL", "").rstrip("/")
        self.bucket = os.environ.get("SOURCE_STORAGE_BUCKET", "")
        self._key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "")

        if not self.url or not self.bucket or not self._key:
            raise StoragePermissionError(
                "Supabase Storage is not configured. "
                "Set SUPABASE_URL, SOURCE_STORAGE_BUCKET, and SUPABASE_SERVICE_ROLE_KEY."
            )
        # Lazy-import supabase SDK
        try:
            from supabase import create_client  # type: ignore
            self._client = create_client(self.url, self._key)
        except ImportError:
            raise StorageUnavailableError(
                "supabase-py is not installed. Run: pip install supabase"
            )
        logger.info(f"[SupabaseStorage] Initialized for bucket={self.bucket}")

    def _headers(self) -> dict:
        return {"Authorization": f"Bearer [REDACTED]"}  # Never log actual key

    def upload_source(self, storage_key: str, data: bytes, content_type: str = "application/octet-stream") -> None:
        try:
            self._client.storage.from_(self.bucket).upload(
                storage_key, data, {"content-type": content_type, "upsert": "true"}
            )
            logger.info(f"[SupabaseStorage] SOURCE_DURABLE_UPLOAD_SUCCESS key={storage_key} size={len(data)}")
        except Exception as e:
            err = str(e)
            if "401" in err or "403" in err or "auth" in err.lower():
                raise StoragePermissionError("Supabase Storage: authentication/permission failure")
            raise StorageUploadError(f"Supabase upload failed: {type(e).__name__}") from e

    def source_exists(self, storage_key: str) -> bool:
        try:
            files = self._client.storage.from_(self.bucket).list(str(Path(storage_key).parent))
            target = Path(storage_key).name
            return any(f.get("name") == target for f in (files or []))
        except Exception as e:
            err = str(e)
            if "401" in err or "403" in err or "auth" in err.lower():
                raise StoragePermissionError("Supabase Storage: authentication/permission failure")
            raise StorageUnavailableError(f"Supabase existence check failed: {type(e).__name__}") from e

    def get_source_metadata(self, storage_key: str) -> Optional[dict]:
        try:
            files = self._client.storage.from_(self.bucket).list(str(Path(storage_key).parent))
            target = Path(storage_key).name
            for f in (files or []):
                if f.get("name") == target:
                    return {"size": f.get("metadata", {}).get("size"), "content_type": f.get("metadata", {}).get("mimetype")}
            return None
        except Exception:
            return None

    def download_source(self, storage_key: str) -> bytes:
        try:
            response = self._client.storage.from_(self.bucket).download(storage_key)
            if not response:
                raise StorageKeyNotFoundError("Supabase returned empty response for key")
            logger.info(f"[SupabaseStorage] SOURCE_RESTORE_SUCCESS key={storage_key}")
            return bytes(response)
        except StorageKeyNotFoundError:
            raise
        except Exception as e:
            err = str(e)
            if "404" in err or "not found" in err.lower():
                raise StorageKeyNotFoundError("Source key not found in Supabase Storage")
            if "401" in err or "403" in err or "auth" in err.lower():
                raise StoragePermissionError("Supabase Storage: authentication/permission failure")
            raise StorageDownloadError(f"Supabase download failed: {type(e).__name__}") from e

    def delete_source(self, storage_key: str) -> None:
        try:
            self._client.storage.from_(self.bucket).remove([storage_key])
        except Exception as e:
            err = str(e)
            if "401" in err or "403" in err or "auth" in err.lower():
                raise StoragePermissionError("Supabase Storage: authentication/permission failure")
            raise StorageUnavailableError(f"Supabase delete failed: {type(e).__name__}") from e


# ── Factory ───────────────────────────────────────────────────────────────────

_provider_instance: Optional[SourceStorage] = None


def get_storage_provider() -> SourceStorage:
    """
    Return the configured storage provider (singleton).

    Provider selection via env var SOURCE_STORAGE_PROVIDER:
        'supabase' → SupabaseStorageProvider (requires credentials)
        'local'    → LocalPersistentStorageProvider (default)
    """
    global _provider_instance
    if _provider_instance is not None:
        return _provider_instance

    provider_name = os.environ.get("SOURCE_STORAGE_PROVIDER", "local").lower().strip()

    if provider_name == "supabase":
        try:
            _provider_instance = SupabaseStorageProvider()
            logger.info("[Storage] Using SupabaseStorageProvider")
        except (StoragePermissionError, StorageUnavailableError) as e:
            logger.warning(f"[Storage] Supabase provider failed ({e}). Falling back to LocalPersistentStorageProvider.")
            _provider_instance = LocalPersistentStorageProvider()
    else:
        _provider_instance = LocalPersistentStorageProvider()
        logger.info("[Storage] Using LocalPersistentStorageProvider")

    return _provider_instance


def reset_storage_provider() -> None:
    """Reset provider singleton (for testing)."""
    global _provider_instance
    _provider_instance = None
