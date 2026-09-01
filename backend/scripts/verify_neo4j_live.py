import sys
import os
from neo4j import GraphDatabase

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app.core.config import settings

def check_neo4j():
    print("=== NEO4J AURA LIVE VERIFICATION ===")
    
    # We use +ssc for self-signed certificates or mocked TLS endpoints to ensure connectivity
    uri = settings.NEO4J_URI.replace("+s://", "+ssc://")
    print(f"Connecting to: {uri} (Using SSC fallback for mocked/test environments)")
    
    try:
        driver = GraphDatabase.driver(uri, auth=(settings.NEO4J_USER, settings.NEO4J_PASSWORD))
        driver.verify_connectivity()
        print("PASS: Connected to Neo4j Aura successfully.")
        
        with driver.session() as session:
            # 1. Database Info Check
            info = session.run("CALL db.info()").single()
            print("Database Name:", info.get("name", "N/A"))
            
            # 2. Constraints Check
            print("\n--- Constraints ---")
            constraints = session.run("SHOW CONSTRAINTS").data()
            if not constraints:
                print("No constraints found. (Expected if relying purely on MERGE without init scripts)")
            else:
                for c in constraints:
                    print(f" - {c.get('name')}: {c.get('type')}")
                    
            # 3. Indexes Check
            print("\n--- Indexes ---")
            indexes = session.run("SHOW INDEXES").data()
            if not indexes:
                print("No indexes found.")
            else:
                for i in indexes:
                    if i.get('type') != 'LOOKUP': # Filter out default lookup indexes
                        print(f" - {i.get('name')}: {i.get('type')}")
        driver.close()
    except Exception as e:
        print(f"FAIL: Neo4j connectivity or query failed.")
        print(e)

if __name__ == "__main__":
    check_neo4j()
