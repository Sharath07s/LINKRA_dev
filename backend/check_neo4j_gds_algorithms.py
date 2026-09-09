import os
from dotenv import load_dotenv
from neo4j import GraphDatabase

load_dotenv()

uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
user = os.getenv("NEO4J_USER", "neo4j")
password = os.getenv("NEO4J_PASSWORD", "password")

driver = GraphDatabase.driver(uri, auth=(user, password))

def test_gds():
    with driver.session() as session:
        try:
            print("Cleaning up old graphs...")
            session.run("CALL gds.graph.drop('testGraph', false)")
            
            print("Projecting graph...")
            session.run("CALL gds.graph.project('testGraph', 'CanonicalEntity', 'EntityRelationship')")
            print("Project succeeded!")
            
            print("Running Louvain...")
            result = session.run("CALL gds.louvain.stream('testGraph') YIELD nodeId, communityId RETURN nodeId, communityId LIMIT 5")
            records = [record for record in result]
            print(f"Louvain succeeded! First 5: {records}")
            
        except Exception as e:
            print(f"GDS Error: {e}")

if __name__ == "__main__":
    test_gds()
    driver.close()
