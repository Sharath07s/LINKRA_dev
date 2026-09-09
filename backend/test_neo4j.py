import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app.ai.neo4j.intelligence import neo4j_intelligence

def test_neo4j():
    print("Testing neo4j...")
    try:
        session = neo4j_intelligence.get_session()
        print("Session acquired!")
        result = session.run("RETURN 1")
        print("Result:", result.single())
        session.close()
    except Exception as e:
        print("Error:", e)

if __name__ == "__main__":
    test_neo4j()
