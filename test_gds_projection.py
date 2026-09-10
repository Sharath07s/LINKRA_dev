import os
from neo4j import GraphDatabase
from dotenv import load_dotenv

load_dotenv("backend/.env")

uri = os.environ.get("NEO4J_URI")
user = os.environ.get("NEO4J_USER")
password = os.environ.get("NEO4J_PASSWORD")

driver = GraphDatabase.driver(uri, auth=(user, password))

def test_gds_projection():
    with driver.session() as session:
        print("Testing GDS Named Graph Projection...")
        
        # Cleanup any existing
        try:
            session.run("CALL gds.graph.drop('test_graph', false)")
        except:
            pass

        try:
            # Try named projection
            result = session.run("""
            CALL gds.graph.project(
                'test_graph',
                'CanonicalEntity',
                ['ASSOCIATED_WITH', 'CONNECTED_TO', 'USES']
            )
            YIELD graphName, nodeProjection, nodeCount, relationshipCount
            RETURN graphName, nodeCount, relationshipCount
            """)
            record = result.single()
            print(f"Named Projection Created: {record['graphName']} Nodes: {record['nodeCount']} Rels: {record['relationshipCount']}")
            
            # Now run louvain on it
            print("Running Louvain on named projection...")
            res = session.run("""
            CALL gds.louvain.stream('test_graph')
            YIELD nodeId, communityId
            RETURN gds.util.asNode(nodeId).name AS name, communityId
            LIMIT 5
            """)
            for r in res:
                print(f"- {r['name']} in community {r['communityId']}")
                
        except Exception as e:
            print(f"Named Projection Error: {e}")

test_gds_projection()
driver.close()
