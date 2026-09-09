"""
tests/test_relationship_sync.py
========================================
Phase 5: Tests for Neo4j relationship synchronization and idempotency.
Checks that relationships are synced exactly once and duplicate 
ingestions do not create duplicate edges.
"""
import uuid
import pytest
from unittest.mock import patch, MagicMock
from app.nlp.relationship.extractor import _sync_to_neo4j
from app.models.relationship import EntityRelationship

def test_sync_to_neo4j_calls_merge_with_correct_properties():
    # Setup mock relationship
    rel = EntityRelationship(
        id=uuid.uuid4(),
        source_entity_id=uuid.uuid4(),
        target_entity_id=uuid.uuid4(),
        relationship_type="ASSOCIATED_WITH",
        confidence=0.85,
        evidence_text="Test evidence",
        extraction_method="llm_semantic",
        ingestion_job_id=uuid.uuid4(),
        source_page=2,
        source_row=None,
        event_timestamp=None
    )

    mock_session = MagicMock()
    mock_tx = MagicMock()
    mock_session.__enter__.return_value = mock_tx
    
    with patch("app.nlp.relationship.extractor.neo4j_intelligence.get_session") as mock_get_session:
        mock_get_session.return_value = mock_session
        _sync_to_neo4j([rel])

    assert mock_tx.run.call_count == 1
    
    call_args = mock_tx.run.call_args
    query_string = call_args[0][0]
    query_params = call_args[0][1]

    # Verify idempotency key is used (MERGE with id)
    assert "MERGE (a)-[r:ASSOCIATED_WITH {id: $rel_id}]->(b)" in query_string
    
    # Verify properties
    assert query_params["rel_id"] == str(rel.id)
    assert query_params["source_id"] == str(rel.source_entity_id)
    assert query_params["target_id"] == str(rel.target_entity_id)
    assert query_params["confidence"] == 0.85
    assert query_params["extraction_method"] == "llm_semantic"
    assert query_params["source_page"] == 2
    assert query_params["ingestion_job_id"] == str(rel.ingestion_job_id)


def test_sync_to_neo4j_skips_empty_list():
    with patch("app.nlp.relationship.extractor.neo4j_intelligence.get_session") as mock_get_session:
        _sync_to_neo4j([])
        
    mock_get_session.assert_not_called()
