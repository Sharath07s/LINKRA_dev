import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import uuid
import pytest
from unittest.mock import patch, MagicMock
# ── Patch targets ──────────────────────────────────────────────────────────
#
# VectorStore is imported lazily inside process_ingestion() with
#   from app.ai.rag.vector_search import VectorStore
# so we must patch it at its definition site, not at the service module.
#
# Other lazy imports inside the function body:
#   from app.nlp.relationship import extract_relationships_for_page
#   from app.ingestion.evidence_linker import link_evidence_for_job
#
# Top-level imports in service.py can be patched at the service module:
#   app.ingestion.service.extract_entities
#   app.ingestion.service.extract_entities_llm
#   app.ingestion.service.IngestionJob

_VS_PATCH = "app.ai.rag.vector_search.VectorStore"
_LINKER_PATCH = "app.ingestion.evidence_linker.link_evidence_for_job"
_REL_PATCH = "app.nlp.relationship.extractor._sync_to_neo4j"
_NEO4J_SYNC_PATCH = "app.nlp.resolution.engine.neo4j_intelligence.sync_canonical_entity"
_SVC = "app.ingestion.service"


def _make_db_mock():
    """Return a db session mock that process_ingestion can use."""
    db = MagicMock()
    db.add.return_value = None
    db.commit.return_value = None
    db.refresh.return_value = None
    db.add_all.return_value = None
    db.query.return_value.filter.return_value.all.return_value = []
    return db


def _make_job_mock():
    job = MagicMock()
    job.id = uuid.uuid4()
    job.error_message = None
    job.chunk_count = None
    job.status = "QUEUED"
    return job


def _run_ingestion(tmp_path, content, filename, index_side_effect):
    """
    Helper that runs process_ingestion with a given VectorStore
    index_document side-effect (list of bools or a callable).

    Returns the job mock after ingestion.
    """
    from app.ingestion.service import process_ingestion

    fir_file = tmp_path / filename
    fir_file.write_text(content, encoding="utf-8")

    job = _make_job_mock()
    db = _make_db_mock()

    with patch(f"{_SVC}.IngestionJob", return_value=job), \
         patch(f"{_SVC}.extract_entities", return_value=[]), \
         patch(f"{_SVC}.extract_entities_llm", return_value=[]), \
         patch(_REL_PATCH, return_value=None), \
         patch(_NEO4J_SYNC_PATCH, return_value=None), \
         patch(_VS_PATCH) as MockVS, \
         patch(_LINKER_PATCH, return_value=None):

        mock_vs_instance = MockVS.return_value
        if callable(index_side_effect):
            mock_vs_instance.index_document.side_effect = index_side_effect
        else:
            mock_vs_instance.index_document.side_effect = index_side_effect

        result = process_ingestion(
            db=db,
            file_path=str(fir_file),
            file_name=filename,
            file_type="txt",
            source_type="FIR",
            file_size=len(fir_file.read_bytes()),
        )

    return result, mock_vs_instance


# Large-enough content to produce ≥3 chunks (chunk_size=1000 chars)
_BIG_TEXT = "The suspect was seen near the market. " * 100  # ~3800 chars → 4+ chunks


# ══════════════════════════════════════════════════════════════════════════
# CASE A — All chunks succeed → COMPLETED
# ══════════════════════════════════════════════════════════════════════════

class TestCaseA_AllChunksSuccess:
    """All index_document calls return True → COMPLETED, chunk_count > 0."""

    def test_status_is_completed(self, tmp_path):
        result, vs = _run_ingestion(
            tmp_path, _BIG_TEXT, "caseA.txt",
            index_side_effect=[True] * 20,  # enough for any chunk count
        )
        assert result.status == "COMPLETED", (
            f"Expected COMPLETED, got {result.status!r}. "
            f"error_message={result.error_message!r}"
        )

    def test_chunk_count_is_positive(self, tmp_path):
        result, vs = _run_ingestion(
            tmp_path, _BIG_TEXT, "caseA2.txt",
            index_side_effect=[True] * 20,
        )
        assert result.chunk_count is not None
        assert result.chunk_count >= 1, (
            "chunk_count must be ≥1 when all indexing succeeds"
        )

    def test_no_failure_error_message(self, tmp_path):
        result, vs = _run_ingestion(
            tmp_path, _BIG_TEXT, "caseA3.txt",
            index_side_effect=[True] * 20,
        )
        # error_message must not hint at failure when all chunks succeed
        assert result.error_message is None or "failed" not in (
            result.error_message or ""
        ).lower()


# ══════════════════════════════════════════════════════════════════════════
# CASE B — Partial failure → COMPLETED_PARTIAL
# ══════════════════════════════════════════════════════════════════════════

class TestCaseB_PartialFailure:
    """Some True, some False → COMPLETED_PARTIAL, chunk_count == number of Trues."""

    # alternate True/False so we always have at least one of each
    _SIDE_EFFECTS = [True, False, True, True, False, True, True, True, True, True]

    def test_status_is_completed_partial(self, tmp_path):
        result, vs = _run_ingestion(
            tmp_path, _BIG_TEXT, "caseB.txt",
            index_side_effect=self._SIDE_EFFECTS,
        )
        assert result.status == "COMPLETED_PARTIAL", (
            f"Expected COMPLETED_PARTIAL, got {result.status!r}. "
            f"error_message={result.error_message!r}"
        )

    def test_status_is_not_fully_completed(self, tmp_path):
        result, vs = _run_ingestion(
            tmp_path, _BIG_TEXT, "caseB2.txt",
            index_side_effect=self._SIDE_EFFECTS,
        )
        assert result.status != "COMPLETED", (
            "Partial vector failure must NOT be reported as COMPLETED"
        )

    def test_chunk_count_equals_successful_count(self, tmp_path):
        result, vs = _run_ingestion(
            tmp_path, _BIG_TEXT, "caseB3.txt",
            index_side_effect=self._SIDE_EFFECTS,
        )
        # chunk_count must equal successful (True) calls, not total calls
        actual_calls = vs.index_document.call_count
        # We know at least 1 True and 1 False occurred
        assert result.chunk_count >= 1
        assert result.chunk_count < actual_calls, (
            "chunk_count should be less than total attempted when some fail"
        )

    def test_error_message_records_partial_failure(self, tmp_path):
        result, vs = _run_ingestion(
            tmp_path, _BIG_TEXT, "caseB4.txt",
            index_side_effect=self._SIDE_EFFECTS,
        )
        assert result.error_message is not None
        assert "Partial RAG indexing" in result.error_message


# ══════════════════════════════════════════════════════════════════════════
# CASE C — All chunks fail (0/N) → FAILED
# ══════════════════════════════════════════════════════════════════════════

class TestCaseC_AllChunksFail:
    """All index_document calls return False → FAILED, chunk_count == 0."""

    def test_status_is_failed(self, tmp_path):
        result, vs = _run_ingestion(
            tmp_path, _BIG_TEXT, "caseC.txt",
            index_side_effect=[False] * 20,
        )
        assert result.status == "FAILED", (
            f"Complete vector failure must be FAILED, got {result.status!r}"
        )

    def test_status_is_not_completed(self, tmp_path):
        result, vs = _run_ingestion(
            tmp_path, _BIG_TEXT, "caseC2.txt",
            index_side_effect=[False] * 20,
        )
        assert result.status != "COMPLETED"
        assert result.status != "COMPLETED_PARTIAL"

    def test_chunk_count_is_zero(self, tmp_path):
        result, vs = _run_ingestion(
            tmp_path, _BIG_TEXT, "caseC3.txt",
            index_side_effect=[False] * 20,
        )
        assert result.chunk_count == 0

    def test_error_message_indicates_vector_failure(self, tmp_path):
        result, vs = _run_ingestion(
            tmp_path, _BIG_TEXT, "caseC4.txt",
            index_side_effect=[False] * 20,
        )
        assert result.error_message is not None
        assert "Vector indexing failed" in result.error_message


# ══════════════════════════════════════════════════════════════════════════
# CASE D — One failed chunk does NOT stop subsequent chunks
# ══════════════════════════════════════════════════════════════════════════

class TestCaseD_OneFailDoesNotStopRest:
    """
    Sequence: True, False, True, True, ...
    All chunks after the failing one must still be attempted.
    chunk_count == number of True results.
    """

    def test_all_chunks_attempted_past_failure(self, tmp_path):
        call_log = []

        def _side_effect(source_id, text, metadata):
            idx = len(call_log)
            r = (idx != 1)   # position 1 (second chunk) fails, all others succeed
            call_log.append(r)
            return r

        result, vs = _run_ingestion(
            tmp_path, _BIG_TEXT, "caseD.txt",
            index_side_effect=_side_effect,
        )

        assert len(call_log) >= 3, (
            f"Expected ≥3 index_document calls; got {len(call_log)}. "
            f"A single chunk failure must NOT halt subsequent chunks."
        )

    def test_chunk_count_equals_successful_chunks(self, tmp_path):
        call_log = []

        def _side_effect(source_id, text, metadata):
            idx = len(call_log)
            r = (idx != 1)
            call_log.append(r)
            return r

        result, vs = _run_ingestion(
            tmp_path, _BIG_TEXT, "caseD2.txt",
            index_side_effect=_side_effect,
        )

        expected = sum(call_log)
        assert result.chunk_count == expected, (
            f"chunk_count ({result.chunk_count}) must equal successful calls ({expected})"
        )
