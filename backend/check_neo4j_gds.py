import asyncio
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
            print("Testing gds.graph.list()...")
            result = session.run("CALL gds.graph.list() YIELD graphName RETURN graphName")
            graphs = [record["graphName"] for record in result]
            print(f"Graphs found: {graphs}")
            
            print("Testing gds.graph.project()...")
            # Try to project a dummy graph
            session.run("CALL gds.graph.project('testGraph', 'Entity', 'RELATES_TO')")
            print("Project succeeded!")
        except Exception as e:
            print(f"GDS Error: {e}")

if __name__ == "__main__":
    test_gds()
    driver.close()
