import os
import sys
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
from app.db.neo4j import neo4j_conn

def check_gds():
    try:
        with neo4j_conn.get_session() as session:
            # Check GDS 
            result = session.run("CALL gds.graph.list()")
            records = list(result)
            print(f"GDS is installed. Graphs: {len(records)}")
    except Exception as e:
        print(f"GDS not available or error: {e}")

if __name__ == "__main__":
    check_gds()
