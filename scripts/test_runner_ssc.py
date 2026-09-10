"""
Test Neo4jQueryRunner directly to reproduce the routing error.
"""
import os
from dotenv import load_dotenv
from graphdatascience.query_runner.neo4j_query_runner import Neo4jQueryRunner

def main():
    load_dotenv()
    
    endpoint = "neo4j+ssc://f725a8a2.databases.neo4j.io"
    user = os.getenv("NEO4J_USER")
    password = os.getenv("NEO4J_PASSWORD")
    
    print("Testing Neo4jQueryRunner.create_for_db")
    try:
        runner = Neo4jQueryRunner.create_for_db(
            endpoint=endpoint,
            auth=(user, password),
            aura_ds=True,
            show_progress=False,
            database=user,
        )
        runner.verify_connectivity()
        print("verify_connectivity: PASS")
    except Exception as e:
        print(f"FAILED: {type(e).__name__}: {e}")

if __name__ == "__main__":
    main()
