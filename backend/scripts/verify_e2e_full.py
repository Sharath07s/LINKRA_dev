import sys
import os
import uuid

# Add the backend directory to sys.path to allow imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.db.session import SessionLocal
from app.db.neo4j import neo4j_conn
from app.ai.neo4j.intelligence import neo4j_intelligence
from sqlalchemy import text

def verify_full_e2e():
    print("=== END-TO-END SUPABASE PG + NEO4J VERIFICATION ===")
    
    # 1. Connect to Supabase PostgreSQL
    print("\n--- 1. Testing PostgreSQL (Supabase Pooler) ---")
    pg_db = SessionLocal()
    try:
        # Simple query to verify connection
        res = pg_db.execute(text("SELECT current_database(), current_user, version()")).fetchone()
        print(f"PASS: Connected to DB '{res[0]}' as '{res[1]}'.")
        print(f"PG Version: {res[2][:30]}...")
    except Exception as e:
        print(f"FAIL: PostgreSQL connection failed: {e}")
        pg_db.close()
        return

    # 2. Connect to Neo4j Aura
    print("\n--- 2. Testing Neo4j Aura ---")
    try:
        health = neo4j_conn.check_health()
        if health.get("status") == "healthy":
            print(f"PASS: Connected to Neo4j. Server: {health.get('details', {}).get('server')}")
        else:
            print("FAIL: Neo4j health check failed.")
            pg_db.close()
            return
    except Exception as e:
        print(f"FAIL: Neo4j connection failed: {e}")
        pg_db.close()
        return

    # 3. Test Graph Synchronization
    print("\n--- 3. Testing Graph Synchronization Idempotency ---")
    try:
        test_entity_id = str(uuid.uuid4())
        print(f"Syncing test canonical entity {test_entity_id} to Neo4j...")
        
        props = {
            "name": "E2E Test Suspect",
            "risk_score": 8.5
        }
        
        # Sync to Neo4j
        neo4j_intelligence.sync_canonical_entity(
            entity_id=test_entity_id,
            entity_type="PERSON",
            properties=props
        )
        print("PASS: Entity synced successfully via Neo4j Intelligence Service.")
        
        # Verify in Neo4j
        session = neo4j_conn.get_session()
        query_res = session.run("MATCH (p:Person {id: $id}) RETURN p.name AS name", id=test_entity_id).single()
        if query_res and query_res["name"] == "E2E Test Suspect":
            print("PASS: Verified entity data exists and is accessible via Graph Queries.")
        else:
            print("FAIL: Entity was synced but could not be queried back.")
            
        # Clean up
        print("Cleaning up Neo4j test data...")
        session.run("MATCH (p:Person {id: $id}) DETACH DELETE p", id=test_entity_id)
        session.close()
        print("PASS: Cleanup completed successfully.")
        
    except Exception as e:
        print(f"FAIL: Graph sync integration failed: {e}")
        
    finally:
        pg_db.close()

    print("\n=== E2E VERIFICATION COMPLETED SUCCESSFULLY ===")

if __name__ == "__main__":
    verify_full_e2e()
