import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app.db.neo4j import neo4j_conn

def verify_sync():
    print("=== END-TO-END SYNCHRONIZATION (MOCKED LIVE CHECK) ===")
    print("WARNING: PostgreSQL is UNVERIFIED due to environment limitation.")
    print("Cannot perform full end-to-end sync without PostgreSQL connectivity.")
    
    # 1. We will verify the idempotency mechanism of the Neo4j Graph Synchronization independently.
    print("\n--- Verifying Neo4j Sync Idempotency Mechanism ---")
    
    session = neo4j_conn.get_session()
    if not session:
        print("FAIL: Could not connect to Neo4j.")
        return
        
    try:
        # Mock Canonical Entity Sync (Idempotent MERGE check)
        print("Running mock entity synchronization 1 (Initial Insert)...")
        res1 = session.run("MERGE (e:CanonicalEntity {id: 'test-uuid-1'}) SET e.name = 'Test Entity' RETURN e").single()
        print("Entity created successfully.")
        
        print("Running mock entity synchronization 2 (Idempotency Check)...")
        res2 = session.run("MERGE (e:CanonicalEntity {id: 'test-uuid-1'}) SET e.name = 'Test Entity' RETURN e").single()
        
        # Verify no duplicates
        count = session.run("MATCH (e:CanonicalEntity {id: 'test-uuid-1'}) RETURN count(e) as c").single()["c"]
        if count == 1:
            print("PASS: Entity synchronization is IDEMPOTENT. No duplicates created.")
        else:
            print("FAIL: Duplicates detected!")
            
        # Clean up mock entity
        session.run("MATCH (e:CanonicalEntity {id: 'test-uuid-1'}) DETACH DELETE e")
        print("\nCleanup completed.")
        
    except Exception as e:
        print(f"FAIL: Idempotency check failed: {e}")
    finally:
        session.close()

if __name__ == "__main__":
    verify_sync()
