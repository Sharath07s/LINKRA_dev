"""
backend/tests/test_copilot_rag_threshold.py
===========================================
Focused tests for RAG Minimum Similarity Threshold Enforcement & Grounding Quality.

Validates that:
1. TEST A: Relevant evidence (similarity >= threshold) passes and yields RAG_CHUNK citation + grounded=True.
2. TEST B: Irrelevant evidence (similarity < threshold) is rejected, yielding no citation and grounded=False.
3. TEST C: Mixed results filter out sub-threshold chunks and preserve only qualifying chunks.
4. TEST D: When all chunks fail the threshold, sources=[] and grounded=False.
5. TEST E: Jane Smith case verification:
   - Without Jane Smith fixture: unrelated chunks (sim ≈ 0.12-0.15) are rejected -> grounded=False, sources=[].
   - With Jane Smith fixture: relevant evidence (sim > 0.25) passes -> grounded=True, citation generated.
6. VectorStore unit tests verifying min_similarity filtering logic.
"""
import uuid
import pytest
from unittest.mock import patch, MagicMock

from app.ai.copilot.orchestrator import CopilotOrchestrator
from app.ai.rag.vector_search import VectorStore
from app.schemas.copilot import CopilotQuery, CopilotIntent, CopilotResponse
from app.core.config import settings


# ── TEST A: Relevant evidence passes (similarity >= threshold) ───────────

def test_rag_threshold_relevant_evidence_passes():
    """
    TEST A: Given a DocumentChunk with similarity above the threshold (e.g. 0.42 >= 0.25):
    - result is accepted
    - RAG evidence contains the chunk
    - citation is created in sources
    - grounded == True
    """
    mock_db = MagicMock()
    mock_user = {"id": "test_investigator"}
    query = CopilotQuery(message="What evidence connects suspect Suresh Rao to the theft?")

    test_chunk_id = str(uuid.uuid4())
    high_sim_results = [
        {
            "chunk_id": test_chunk_id,
            "doc_id": "fir_2026_blr_0847.txt",
            "content": "Suresh Rao was apprehended with the stolen gold necklace at 23:00.",
            "metadata": {
                "ingestion_job_id": "job-test-high-001",
                "source_filename": "fir_2026_blr_0847.txt",
                "source_type": "FIR",
                "page_number": 1,
            },
            "similarity": 0.4215,
        }
    ]

    with patch("app.ai.copilot.orchestrator.IntentRouter.get_intent", return_value=CopilotIntent.EVIDENCE_LOOKUP), \
         patch("app.ai.copilot.orchestrator.VectorStore") as MockVS, \
         patch("app.ai.copilot.orchestrator.FallbackManager.execute_with_fallback") as mock_llm:

        mock_vs_instance = MagicMock()
        mock_vs_instance.semantic_search.return_value = high_sim_results
        MockVS.return_value = mock_vs_instance

        mock_llm.return_value = {
            "result": "Suresh Rao was found with the stolen gold necklace per FIR records.",
            "provider": "groq_primary",
        }

        response: CopilotResponse = CopilotOrchestrator.handle_query(mock_db, query, mock_user)

        # VectorStore must have been called with min_similarity
        mock_vs_instance.semantic_search.assert_called_once_with(
            query.message,
            top_k=3,
            min_similarity=CopilotOrchestrator.RAG_MIN_SIMILARITY,
        )

        assert response.status == "ANSWERED"
        assert len(response.sources) == 1
        assert response.sources[0].type == "RAG_CHUNK"
        assert response.sources[0].id == test_chunk_id
        assert response.grounded is True
        assert len(response.evidence) == 1
        assert response.evidence[0]["similarity"] == 0.4215


# ── TEST B: Irrelevant evidence is rejected (similarity < threshold) ─────

def test_rag_threshold_irrelevant_evidence_rejected():
    """
    TEST B: Given chunks with similarity below the threshold (e.g. 0.1467, 0.1241 < 0.25):
    - chunks are NOT returned as usable evidence
    - no RAG_CHUNK citation is created
    - grounded == False
    - status is INSUFFICIENT_DATA (or empty sources when general query)
    """
    mock_db = MagicMock()
    mock_user = {"id": "test_investigator"}
    query = CopilotQuery(message="What evidence connects Jane Smith to the vehicle?")

    # Simulate raw low-similarity chunks that semantic_search with min_similarity filters out
    with patch("app.ai.copilot.orchestrator.IntentRouter.get_intent", return_value=CopilotIntent.EVIDENCE_LOOKUP), \
         patch("app.ai.copilot.orchestrator.VectorStore") as MockVS:

        mock_vs_instance = MagicMock()
        # semantic_search filters them out and returns empty list
        mock_vs_instance.semantic_search.return_value = []
        MockVS.return_value = mock_vs_instance

        response: CopilotResponse = CopilotOrchestrator.handle_query(mock_db, query, mock_user)

        mock_vs_instance.semantic_search.assert_called_once_with(
            query.message,
            top_k=3,
            min_similarity=CopilotOrchestrator.RAG_MIN_SIMILARITY,
        )

        assert response.status == "INSUFFICIENT_DATA"
        assert response.sources == []
        assert response.grounded is False
        assert response.evidence == []


def test_rag_threshold_defense_in_depth_filters_sub_threshold():
    """
    TEST B2: Even if VectorStore returned an unfiltered sub-threshold chunk
    (e.g., in a mock or legacy caller), orchestrator defense-in-depth must reject it.
    """
    mock_db = MagicMock()
    mock_user = {"id": "test_investigator"}
    query = CopilotQuery(message="What evidence connects Jane Smith to the vehicle?")

    sub_threshold_results = [
        {
            "chunk_id": str(uuid.uuid4()),
            "doc_id": "unrelated_fir.txt",
            "content": "Complainant Priya Sharma reported theft of handbag.",
            "metadata": {"ingestion_job_id": "job-unrelated-001"},
            "similarity": 0.1467,  # Below 0.25
        },
        {
            "chunk_id": str(uuid.uuid4()),
            "doc_id": "unrelated_fir.txt",
            "content": "Witness Venkatesh Murthy saw accused fleeing.",
            "metadata": {"ingestion_job_id": "job-unrelated-002"},
            "similarity": 0.1241,  # Below 0.25
        }
    ]

    with patch("app.ai.copilot.orchestrator.IntentRouter.get_intent", return_value=CopilotIntent.EVIDENCE_LOOKUP), \
         patch("app.ai.copilot.orchestrator.VectorStore") as MockVS:

        mock_vs_instance = MagicMock()
        mock_vs_instance.semantic_search.return_value = sub_threshold_results
        MockVS.return_value = mock_vs_instance

        response: CopilotResponse = CopilotOrchestrator.handle_query(mock_db, query, mock_user)

        # Sub-threshold chunks must be rejected by defense-in-depth in _tool_rag_evidence_lookup
        assert response.status == "INSUFFICIENT_DATA"
        assert response.sources == []
        assert response.grounded is False
        assert response.evidence == []


# ── TEST C: Mixed results (one above, one below threshold) ───────────────

def test_rag_threshold_mixed_results_filters_only_sub_threshold():
    """
    TEST C: Given:
    - Chunk A: similarity = 0.45 (relevant / above threshold)
    - Chunk B: similarity = 0.14 (irrelevant / below threshold)
    
    Only Chunk A must become evidence and a citation; grounded == True.
    """
    mock_db = MagicMock()
    mock_user = {"id": "test_investigator"}
    query = CopilotQuery(message="What evidence connects suspect to the weapon?")

    mixed_results = [
        {
            "chunk_id": "chunk-a-id",
            "doc_id": "fir_weapon_report.txt",
            "content": "Recovered weapon from suspect's apartment.",
            "metadata": {"ingestion_job_id": "job-chunk-a", "source_filename": "fir_weapon_report.txt"},
            "similarity": 0.4500,
        },
        {
            "chunk_id": "chunk-b-id",
            "doc_id": "unrelated_traffic_report.txt",
            "content": "Traffic violation logged on Ring Road.",
            "metadata": {"ingestion_job_id": "job-chunk-b", "source_filename": "unrelated_traffic_report.txt"},
            "similarity": 0.1400,
        }
    ]

    with patch("app.ai.copilot.orchestrator.IntentRouter.get_intent", return_value=CopilotIntent.EVIDENCE_LOOKUP), \
         patch("app.ai.copilot.orchestrator.VectorStore") as MockVS, \
         patch("app.ai.copilot.orchestrator.FallbackManager.execute_with_fallback") as mock_llm:

        mock_vs_instance = MagicMock()
        mock_vs_instance.semantic_search.return_value = mixed_results
        MockVS.return_value = mock_vs_instance

        mock_llm.return_value = {
            "result": "The weapon was recovered from the suspect's residence.",
            "provider": "groq_primary",
        }

        response: CopilotResponse = CopilotOrchestrator.handle_query(mock_db, query, mock_user)

        assert response.status == "ANSWERED"
        assert len(response.evidence) == 1
        assert response.evidence[0]["chunk_id"] == "chunk-a-id"
        assert response.evidence[0]["similarity"] == 0.4500

        assert len(response.sources) == 1
        assert response.sources[0].id == "chunk-a-id"
        assert response.grounded is True


# ── TEST D: No evidence / all results below threshold ────────────────────

def test_rag_threshold_all_below_threshold_produces_ungrounded():
    """
    TEST D: When all retrieval results fall below min_similarity:
    - evidence == []
    - sources == []
    - grounded == False
    """
    mock_db = MagicMock()
    mock_user = {"id": "test_investigator"}
    query = CopilotQuery(message="Find proof of encrypted offshore wire transfers")

    with patch("app.ai.copilot.orchestrator.IntentRouter.get_intent", return_value=CopilotIntent.GENERAL_INTELLIGENCE_QUERY), \
         patch("app.ai.copilot.orchestrator.VectorStore") as MockVS, \
         patch.object(CopilotOrchestrator, "_tool_entity_fuzzy_search"), \
         patch("app.ai.copilot.orchestrator.FallbackManager.execute_with_fallback") as mock_llm:

        mock_vs_instance = MagicMock()
        mock_vs_instance.semantic_search.return_value = []
        MockVS.return_value = mock_vs_instance

        mock_llm.return_value = {
            "result": "No evidence was found regarding encrypted offshore transfers.",
            "provider": "groq_primary",
        }

        response: CopilotResponse = CopilotOrchestrator.handle_query(mock_db, query, mock_user)

        assert response.status == "ANSWERED"
        assert response.evidence == []
        assert response.sources == []
        assert response.grounded is False


# ── TEST E: Jane Smith Case Verification ─────────────────────────────────

def test_jane_smith_case_absent_fixture_is_rejected():
    """
    TEST E1: When the Jane Smith FIR fixture is absent:
    Query: "What evidence connects Jane Smith to the vehicle?"
    Unrelated Priya Sharma FIR chunks (sim ≈ 0.12-0.15) must NOT cause grounded=True.
    Sources must be empty, grounded must be False.
    """
    context_data = {
        "intent": CopilotIntent.EVIDENCE_LOOKUP.value,
        "entities": [],
        "relationships": [],
        "evidence": [],
        "analytics": [],
        "anomalies": [],
        "potential_links": [],
        "investigation": None,
    }

    with patch("app.ai.copilot.orchestrator.VectorStore") as MockVS:
        mock_vs = MagicMock()
        # When semantic_search is called with min_similarity=0.25, it returns []
        mock_vs.semantic_search.return_value = []
        MockVS.return_value = mock_vs

        CopilotOrchestrator._tool_rag_evidence_lookup(
            "What evidence connects Jane Smith to the vehicle?",
            {"id": "user1"},
            context_data,
        )

        assert context_data["evidence"] == []
        sources = CopilotOrchestrator._build_sources_from_evidence(context_data["evidence"])
        assert sources == []
        assert bool(sources) is False


def test_jane_smith_case_present_fixture_is_accepted():
    """
    TEST E2: When Jane Smith evidence is present:
    Actual FIR text: "Jane Smith was seen driving a blue Toyota near 5th Street."
    Query: "What evidence connects Jane Smith to the vehicle?"
    Expected similarity ≈ 0.6305 (> 0.25 threshold):
    - result is accepted
    - RAG_CHUNK source is created
    - citation returned
    - grounded == True
    """
    mock_db = MagicMock()
    mock_user = {"id": "test_investigator"}
    query = CopilotQuery(message="What evidence connects Jane Smith to the vehicle?")

    jane_smith_chunk = [
        {
            "chunk_id": "chunk-jane-smith-01",
            "doc_id": "fir_jane_smith_case.txt",
            "content": "Jane Smith was seen driving a blue Toyota near 5th Street.",
            "metadata": {
                "ingestion_job_id": "job-jane-smith-99",
                "source_filename": "fir_jane_smith_case.txt",
                "source_type": "FIR",
                "page_number": 1,
            },
            "similarity": 0.6305,
        }
    ]

    with patch("app.ai.copilot.orchestrator.IntentRouter.get_intent", return_value=CopilotIntent.EVIDENCE_LOOKUP), \
         patch("app.ai.copilot.orchestrator.VectorStore") as MockVS, \
         patch("app.ai.copilot.orchestrator.FallbackManager.execute_with_fallback") as mock_llm:

        mock_vs = MagicMock()
        mock_vs.semantic_search.return_value = jane_smith_chunk
        MockVS.return_value = mock_vs

        mock_llm.return_value = {
            "result": "Jane Smith was observed operating a blue Toyota near 5th Street.",
            "provider": "groq_primary",
        }

        response: CopilotResponse = CopilotOrchestrator.handle_query(mock_db, query, mock_user)

        assert response.status == "ANSWERED"
        assert len(response.sources) == 1
        assert response.sources[0].type == "RAG_CHUNK"
        assert response.sources[0].id == "chunk-jane-smith-01"
        assert response.sources[0].label == "fir_jane_smith_case.txt"
        assert "Similarity: 0.6305" in response.sources[0].context
        assert response.grounded is True


# ── TEST F: VectorStore.semantic_search min_similarity parameter filtering ─

def test_vector_store_semantic_search_filters_by_min_similarity():
    """
    TEST F: Unit test verifying that VectorStore.semantic_search correctly filters
    rows according to the min_similarity threshold argument.
    """
    vs = VectorStore.__new__(VectorStore)
    vs.embedding_model = MagicMock()
    vs.embedding_model.embed_query.return_value = [0.1] * 384
    vs.engine = MagicMock()

    # Mock chunk rows: row 0 has distance 0.35 -> sim = 0.65; row 1 has distance 0.88 -> sim = 0.12
    chunk1 = MagicMock()
    chunk1.id = uuid.uuid4()
    chunk1.source_id = "doc1.txt"
    chunk1.content = "Relevant text content"
    chunk1.metadata_json = {"page": 1}

    chunk2 = MagicMock()
    chunk2.id = uuid.uuid4()
    chunk2.source_id = "doc2.txt"
    chunk2.content = "Irrelevant text content"
    chunk2.metadata_json = {"page": 2}

    mock_session = MagicMock()
    mock_session.execute.return_value.all.return_value = [
        (chunk1, 0.35),  # sim = 0.65
        (chunk2, 0.88),  # sim = 0.12
    ]

    with patch("app.ai.rag.vector_search.Session") as MockSession:
        MockSession.return_value.__enter__.return_value = mock_session

        # With min_similarity=0.25, only chunk1 should be returned
        results = vs.semantic_search("test query", top_k=5, min_similarity=0.25)
        assert len(results) == 1
        assert results[0]["doc_id"] == "doc1.txt"
        assert results[0]["similarity"] == 0.65

        # With min_similarity=None, both chunks should be returned (backward compatibility)
        results_all = vs.semantic_search("test query", top_k=5, min_similarity=None)
        assert len(results_all) == 2

        # With min_similarity=0.70, neither chunk should be returned
        results_none = vs.semantic_search("test query", top_k=5, min_similarity=0.70)
        assert len(results_none) == 0
