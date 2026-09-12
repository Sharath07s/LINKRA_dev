"""
backend/tests/test_copilot_sources.py
======================================
Focused tests for CopilotResponse.sources[] population from context_data["evidence"].

All data in these tests is TEST FIXTURE data, not production data.
No fake production data is created or seeded.
"""
import pytest
from app.ai.copilot.orchestrator import CopilotOrchestrator
from app.schemas.copilot import CopilotCitation


# ── Test 1: Sources populated from RAG evidence ────────────────────────

def test_sources_populated_from_rag_evidence():
    """Given existing RAG evidence, verify sources[] contains corresponding real citation data."""
    evidence = [
        {
            "type": "RAG_CHUNK",
            "title": "fir_2026_blr_0847.txt",
            "description": "Complainant Priya Sharma reported theft of gold necklace.",
            "similarity": 0.8912,
            "metadata": {
                "ingestion_job_id": "abc-123-def-456",
                "source_filename": "fir_2026_blr_0847.txt",
                "source_type": "FIR",
                "page_number": 1,
                "chunk_index": 0,
            },
        }
    ]

    sources = CopilotOrchestrator._build_sources_from_evidence(evidence)

    assert len(sources) == 1
    s = sources[0]
    assert isinstance(s, CopilotCitation)
    assert s.type == "RAG_CHUNK"
    assert s.id == "abc-123-def-456"  # From metadata.ingestion_job_id
    assert s.label == "fir_2026_blr_0847.txt"
    assert "File: fir_2026_blr_0847.txt" in s.context
    assert "Page: 1" in s.context
    assert "Similarity: 0.8912" in s.context
    assert "Source: FIR" in s.context


# ── Test 2: Empty evidence produces empty sources ──────────────────────

def test_empty_evidence_produces_empty_sources():
    """Given empty evidence, verify sources[] is empty. No fabricated citations."""
    evidence = []

    sources = CopilotOrchestrator._build_sources_from_evidence(evidence)

    assert sources == []


# ── Test 3: Multiple evidence items produce matching sources ───────────

def test_multiple_evidence_items_produce_multiple_sources():
    """Given multiple retrieved chunks, verify len(sources) == len(evidence)."""
    evidence = [
        {
            "type": "RAG_CHUNK",
            "title": "doc_a.txt",
            "description": "Content from document A.",
            "similarity": 0.92,
            "metadata": {
                "ingestion_job_id": "job-aaa",
                "source_filename": "doc_a.txt",
                "source_type": "FIR",
                "page_number": 1,
            },
        },
        {
            "type": "RAG_CHUNK",
            "title": "doc_b.pdf",
            "description": "Content from document B.",
            "similarity": 0.85,
            "metadata": {
                "ingestion_job_id": "job-bbb",
                "source_filename": "doc_b.pdf",
                "source_type": "POLICE_REPORT",
                "page_number": 3,
            },
        },
        {
            "type": "ENTITY_EXTRACTION",
            "title": "Extracted as 'Suresh Rao'",
            "description": "Extracted via spacy_ner with 95% confidence.",
            "provenance": {
                "ingestion_job_id": "job-ccc",
                "source_type": "FIR",
                "file_name": "doc_c.txt",
                "file_type": "txt",
                "page": 2,
                "row": None,
            },
        },
    ]

    sources = CopilotOrchestrator._build_sources_from_evidence(evidence)

    assert len(sources) == 3

    # Verify RAG_CHUNK sources
    assert sources[0].type == "RAG_CHUNK"
    assert sources[0].id == "job-aaa"
    assert sources[0].label == "doc_a.txt"

    assert sources[1].type == "RAG_CHUNK"
    assert sources[1].id == "job-bbb"
    assert sources[1].label == "doc_b.pdf"
    assert "Page: 3" in sources[1].context
    assert "Source: POLICE_REPORT" in sources[1].context

    # Verify ENTITY_EXTRACTION source
    assert sources[2].type == "ENTITY_EXTRACTION"
    assert sources[2].id == "job-ccc"
    assert sources[2].label == "Extracted as 'Suresh Rao'"
    assert "File: doc_c.txt" in sources[2].context
    assert "Page: 2" in sources[2].context
    assert "Source: FIR" in sources[2].context


# ── Test 4: Evidence without metadata/provenance still produces valid source ─

def test_evidence_without_metadata_uses_title_as_id():
    """When metadata and provenance are missing, id falls back to title."""
    evidence = [
        {
            "type": "RAG_CHUNK",
            "title": "unknown_doc.txt",
            "description": "Some content.",
            "similarity": 0.75,
        }
    ]

    sources = CopilotOrchestrator._build_sources_from_evidence(evidence)

    assert len(sources) == 1
    assert sources[0].id == "unknown_doc.txt"  # Falls back to title
    assert sources[0].label == "unknown_doc.txt"
    assert "Similarity: 0.75" in sources[0].context


# ── Test 5: Provenance takes priority over metadata for ID ─────────────

def test_provenance_takes_priority_over_metadata_for_id():
    """When both provenance and metadata have ingestion_job_id, provenance wins."""
    evidence = [
        {
            "type": "ENTITY_EXTRACTION",
            "title": "Extracted as 'Test Entity'",
            "description": "Details.",
            "provenance": {
                "ingestion_job_id": "provenance-id-wins",
                "file_name": "from_provenance.txt",
                "source_type": "CDR",
            },
            "metadata": {
                "ingestion_job_id": "metadata-id-loses",
                "source_filename": "from_metadata.txt",
            },
        }
    ]

    sources = CopilotOrchestrator._build_sources_from_evidence(evidence)

    assert sources[0].id == "provenance-id-wins"
    assert "File: from_provenance.txt" in sources[0].context
