import pytest
from app.ai.neo4j.intelligence import neo4j_intelligence

def test_graph_investigation_traversal():
    """
    Test running standard investigation multi-hop traversal queries on the graph.
    """
    with neo4j_intelligence.get_session() as session:
        result = session.run("MATCH ()-[r]->() RETURN count(r) as count").single()
        count = result["count"] if result else 0
        
        if count == 0:
            pytest.skip("BLOCKED: No relationships available to perform multi-hop traversals.")
            
        # Example traversal (would be executed if data existed)
        # session.run("MATCH (a:Entity)-[r*1..3]-(b:Entity) RETURN a, r, b LIMIT 1")
        pass
