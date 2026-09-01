import sys
import os

# Ensure backend directory is in path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.db.neo4j import get_neo4j_session
from app.db.session import SessionLocal
from app.models.crime import Crime

def verify_pipeline():
    print("Verifying E2E Pipeline dependencies (PostgreSQL -> Neo4j)...")
    
    # 1. Check PostgreSQL Connection
    db = SessionLocal()
    try:
        count = db.query(Crime).count()
        print(f"PostgreSQL connection successful. Crimes in DB: {count}")
    except Exception as e:
        print(f"FAILED to query PostgreSQL: {e}")
    finally:
        db.close()
        
    # 2. Check Neo4j Connection
    try:
        session_gen = get_neo4j_session()
        session = next(session_gen)
        if session:
            result = session.run("MATCH (n) RETURN count(n) as node_count")
            node_count = result.single()["node_count"]
            print(f"Neo4j connection successful. Nodes in DB: {node_count}")
            session.close()
        else:
            print("FAILED to get Neo4j session.")
    except Exception as e:
        print(f"FAILED to query Neo4j: {e}")

if __name__ == "__main__":
    verify_pipeline()
