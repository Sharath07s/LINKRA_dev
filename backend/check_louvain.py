import os
import sys
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
from app.db.neo4j import neo4j_conn

def check_louvain():
    try:
        with neo4j_conn.get_session() as session:
            # Drop graph if exists
            try:
                session.run("CALL gds.graph.drop('myGraph', false)")
            except:
                pass
                
            print("Projecting graph...")
            session.run("CALL gds.graph.project('myGraph', 'Entity', '*')")
            print("Graph projected. Running Louvain...")
            result = session.run("""
                CALL gds.louvain.stream('myGraph')
                YIELD nodeId, communityId
                RETURN gds.util.asNode(nodeId).name AS name, communityId
                ORDER BY communityId
            """)
            records = list(result)
            print(f"Louvain finished. Entities clustered: {len(records)}")
            for r in records[:5]:
                print(f"  {r['name']} -> Community {r['communityId']}")
                
            print("Dropping graph...")
            session.run("CALL gds.graph.drop('myGraph')")
    except Exception as e:
        print(f"Louvain error: {e}")

if __name__ == "__main__":
    check_louvain()
