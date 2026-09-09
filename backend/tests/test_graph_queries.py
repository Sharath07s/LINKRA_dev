"""
tests/test_graph_queries.py
========================================
Phase 5: Tests for Graph / Neo4j Intelligence queries.
Checks boundedness, limits, and that correct query logic is used.
"""
import pytest
from unittest.mock import patch, MagicMock

from app.ai.neo4j.intelligence import Neo4jIntelligenceService
from app.ai.neo4j import cypher_queries as queries

def test_get_suspect_network_calls_correct_query():
    svc = Neo4jIntelligenceService()
    mock_session = MagicMock()
    mock_tx = MagicMock()
    
    mock_session.__enter__.return_value = mock_tx
    mock_tx.run.return_value.single.return_value = {"nodes": [], "edges": []}
    
    with patch.object(svc, "get_session", return_value=mock_session):
        res = svc.get_suspect_network("test-id")
        
    mock_tx.run.assert_called_once_with(
        queries.GET_NETWORK_NODES_EDGES,
        entity_id="test-id",
        limit=queries.DEFAULT_NETWORK_LIMIT
    )
    assert res == {"nodes": [], "edges": []}


def test_get_high_risk_network_calls_correct_query():
    svc = Neo4jIntelligenceService()
    mock_session = MagicMock()
    mock_tx = MagicMock()
    
    mock_session.__enter__.return_value = mock_tx
    mock_tx.run.return_value.single.return_value = {"nodes": [], "edges": []}
    
    with patch.object(svc, "get_session", return_value=mock_session):
        res = svc.get_high_risk_network(min_risk=7.5, limit=50)
        
    mock_tx.run.assert_called_once_with(
        queries.GET_HIGH_RISK_NETWORK,
        min_risk=7.5,
        limit=50
    )
    assert res == {"nodes": [], "edges": []}


def test_sync_relationship_sanitizes_type():
    svc = Neo4jIntelligenceService()
    mock_session = MagicMock()
    mock_tx = MagicMock()
    mock_session.__enter__.return_value = mock_tx
    
    malicious_type = "ASSOCIATED_WITH]->(x) DETACH DELETE x //"
    expected_sanitized = "ASSOCIATED_WITHxDETACHDELETEx"
    
    with patch.object(svc, "get_session", return_value=mock_session):
        svc.sync_relationship(
            relationship_id="rel-123",
            source_id="src-1",
            target_id="tgt-1",
            relationship_type=malicious_type,
            properties={"confidence": 0.9}
        )
        
    assert mock_tx.run.call_count == 1
    call_args = mock_tx.run.call_args
    query_string = call_args[0][0]
    
    # Assert the sanitized type made it into the cypher query
    assert f"-[r:{expected_sanitized} " in query_string
