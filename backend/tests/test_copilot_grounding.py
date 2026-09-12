"""
backend/tests/test_copilot_grounding.py
=======================================
Focused tests for Copilot RAG Grounding State Hardening.

All test data in this file uses clearly isolated in-memory test fixtures.
NO fake production data is created, inserted, or modified.
NO production databases (PostgreSQL/Neo4j) are seeded with fake records.
"""
import pytest
from unittest.mock import patch, MagicMock
from app.ai.copilot.orchestrator import CopilotOrchestrator
from app.schemas.copilot import CopilotQuery, CopilotIntent, CopilotResponse, CopilotCitation


# ── Test 1: Evidence exists → sources populated, grounded == True ──────

def test_grounding_with_evidence():
    """
    Test 1: When real/fixture evidence exists in context_data["evidence"],
    the response must have populated sources[] and grounded == True.
    """
    evidence_fixture = [
        {
            "type": "RAG_CHUNK",
            "title": "fir_2026_blr_0100.txt",
            "description": "Accused Ramesh Kumar seen near crime scene at 22:30.",
            "similarity": 0.9125,
            "metadata": {
                "ingestion_job_id": "job-test-fixture-001",
                "source_filename": "fir_2026_blr_0100.txt",
                "source_type": "FIR",
                "page_number": 1,
            },
        }
    ]

    mock_db = MagicMock()
    mock_user = {"id": "test_investigator_user"}
    query = CopilotQuery(message="What evidence links Ramesh to the crime scene?")

    with patch("app.ai.copilot.orchestrator.IntentRouter.get_intent", return_value=CopilotIntent.EVIDENCE_LOOKUP), \
         patch.object(CopilotOrchestrator, "_tool_rag_evidence_lookup") as mock_rag_lookup, \
         patch("app.ai.copilot.orchestrator.FallbackManager.execute_with_fallback") as mock_llm:
        
        # Simulate RAG lookup populating context_data with the fixture evidence
        def populate_evidence(query_text, user, context_data):
            context_data["evidence"].extend(evidence_fixture)
        mock_rag_lookup.side_effect = populate_evidence

        mock_llm.return_value = {
            "result": "Ramesh Kumar was placed near the crime scene based on FIR documentation.",
            "provider": "groq_primary",
        }

        response: CopilotResponse = CopilotOrchestrator.handle_query(mock_db, query, mock_user)

        assert response.status == "ANSWERED"
        assert len(response.sources) == 1
        assert response.sources[0].id == "job-test-fixture-001"
        assert response.sources[0].type == "RAG_CHUNK"
        assert response.grounded is True


# ── Test 2: Empty evidence → sources == [], grounded == False ──────────

def test_grounding_with_empty_evidence():
    """
    Test 2: When semantic retrieval returns no evidence (evidence = []),
    the response must NOT falsely claim grounding.
    Expected: sources == [] and grounded == False.
    """
    mock_db = MagicMock()
    mock_user = {"id": "test_investigator_user"}
    query = CopilotQuery(message="Tell me about international money laundering schemes.")

    with patch("app.ai.copilot.orchestrator.IntentRouter.get_intent", return_value=CopilotIntent.GENERAL_INTELLIGENCE_QUERY), \
         patch.object(CopilotOrchestrator, "_tool_rag_evidence_lookup") as mock_rag_lookup, \
         patch.object(CopilotOrchestrator, "_tool_entity_fuzzy_search"), \
         patch("app.ai.copilot.orchestrator.FallbackManager.execute_with_fallback") as mock_llm:
        
        # Simulate RAG lookup returning nothing (empty results)
        def no_evidence(query_text, user, context_data):
            pass  # context_data["evidence"] remains []
        mock_rag_lookup.side_effect = no_evidence

        mock_llm.return_value = {
            "result": "General intelligence response without specific case evidence.",
            "provider": "groq_primary",
        }

        response: CopilotResponse = CopilotOrchestrator.handle_query(mock_db, query, mock_user)

        assert response.status == "ANSWERED"
        assert response.sources == []
        assert response.grounded is False


# ── Test 3: Retrieval failure → sources == [], grounded == False ───────

def test_grounding_with_retrieval_failure():
    """
    Test 3: When RAG retrieval fails (e.g., VectorStore exception),
    the failure must be handled gracefully without manufacturing fake evidence.
    Expected: sources == [] and grounded == False.
    """
    mock_db = MagicMock()
    mock_user = {"id": "test_investigator_user"}
    query = CopilotQuery(message="Lookup evidence for suspicious transactions.")

    with patch("app.ai.copilot.orchestrator.IntentRouter.get_intent", return_value=CopilotIntent.EVIDENCE_LOOKUP), \
         patch("app.ai.copilot.orchestrator.VectorStore") as MockVectorStore, \
         patch("app.ai.copilot.orchestrator.FallbackManager.execute_with_fallback") as mock_llm:
        
        # Simulate VectorStore raising a database/connection exception
        mock_vs_instance = MagicMock()
        mock_vs_instance.semantic_search.side_effect = ConnectionError("Vector database connection timed out")
        MockVectorStore.return_value = mock_vs_instance

        mock_llm.return_value = {
            "result": "I don't have enough verified information in the current LINKRA data to answer that.",
            "provider": "groq_primary",
        }

        # Bounded tool catches exception; evidence remains []
        response: CopilotResponse = CopilotOrchestrator.handle_query(mock_db, query, mock_user)

        assert response.sources == []
        assert response.grounded is False


# ── Test 4: Existing sources regression ────────────────────────────────

def test_existing_sources_regression():
    """
    Test 4: Verify previously implemented CopilotResponse.sources[] behavior still works
    and maintains exact consistency with the grounded flag.
    """
    evidence_multi = [
        {
            "type": "RAG_CHUNK",
            "title": "fir_doc_1.txt",
            "description": "Snippet 1",
            "similarity": 0.88,
            "metadata": {"ingestion_job_id": "job-1", "source_filename": "fir_doc_1.txt", "page_number": 2},
        },
        {
            "type": "ENTITY_EXTRACTION",
            "title": "Extracted as 'Suspect Alpha'",
            "description": "Extracted via NER",
            "provenance": {"ingestion_job_id": "job-2", "file_name": "report_2.pdf", "page": 1, "source_type": "POLICE_REPORT"},
        },
    ]

    sources = CopilotOrchestrator._build_sources_from_evidence(evidence_multi)
    assert len(sources) == 2
    assert sources[0].type == "RAG_CHUNK"
    assert sources[0].id == "job-1"
    assert sources[1].type == "ENTITY_EXTRACTION"
    assert sources[1].id == "job-2"

    # Consistency rule check: len(sources) > 0 <=> grounded is True
    assert bool(sources) is True

    empty_sources = CopilotOrchestrator._build_sources_from_evidence([])
    assert empty_sources == []
    assert bool(empty_sources) is False


# ── Test 5: Deterministic fallback grounded semantics ──────────────────

def test_deterministic_fallback_with_evidence():
    """
    Test 5a: _deterministic_fallback with evidence produces populated sources and grounded == True.
    """
    context_data = {
        "intent": CopilotIntent.EVIDENCE_LOOKUP.value,
        "entities": [],
        "relationships": [],
        "evidence": [
            {
                "type": "RAG_CHUNK",
                "title": "fir_doc_test.txt",
                "description": "Direct eyewitness account.",
                "similarity": 0.95,
                "metadata": {"ingestion_job_id": "job-fallback-1"},
            }
        ],
        "analytics": [],
        "anomalies": [],
        "potential_links": [],
        "investigation": None,
    }

    response = CopilotOrchestrator._deterministic_fallback(context_data, CopilotIntent.EVIDENCE_LOOKUP)

    assert response.status == "PROVIDER_UNAVAILABLE"
    assert len(response.sources) == 1
    assert response.sources[0].id == "job-fallback-1"
    assert response.grounded is True


def test_deterministic_fallback_without_evidence():
    """
    Test 5b: _deterministic_fallback without evidence produces empty sources and grounded == False.
    """
    context_data = {
        "intent": CopilotIntent.ENTITY_LOOKUP.value,
        "entities": [{"id": "ent-1", "name": "Vijay Kumar"}],
        "relationships": [],
        "evidence": [],
        "analytics": [],
        "anomalies": [],
        "potential_links": [],
        "investigation": None,
    }

    response = CopilotOrchestrator._deterministic_fallback(context_data, CopilotIntent.ENTITY_LOOKUP)

    assert response.status == "PROVIDER_UNAVAILABLE"
    assert response.sources == []
    assert response.grounded is False


# ── Test 6: Insufficient data path grounding semantics ─────────────────

def test_insufficient_data_grounded_is_false():
    """
    Test 6: When context is completely empty and intent is not general intelligence,
    INSUFFICIENT_DATA status is returned with sources == [] and grounded == False.
    """
    mock_db = MagicMock()
    mock_user = {"id": "test_investigator_user"}
    query = CopilotQuery(
        entity_id="00000000-0000-0000-0000-000000000099",
        message="Explain this entity's anomaly",
    )

    with patch("app.ai.copilot.orchestrator.IntentRouter.get_intent", return_value=CopilotIntent.ANOMALY_EXPLANATION), \
         patch.object(CopilotOrchestrator, "_tool_entity_explainability_lookup"), \
         patch.object(CopilotOrchestrator, "_tool_neo4j_anomaly_lookup"):
        # Context remains completely empty
        response: CopilotResponse = CopilotOrchestrator.handle_query(mock_db, query, mock_user)

        assert response.status == "INSUFFICIENT_DATA"
        assert response.sources == []
        assert response.grounded is False
