"""
Test driver connectivity explicitly with neo4j+ssc:// scheme.
"""
import os
from neo4j import GraphDatabase
from dotenv import load_dotenv

def main():
    load_dotenv()
    
    host = "f725a8a2.databases.neo4j.io"
    user = os.getenv("NEO4J_USER")
    password = os.getenv("NEO4J_PASSWORD")
    
    print("Testing neo4j+ssc://")
    try:
        driver = GraphDatabase.driver(f"neo4j+ssc://{host}", auth=(user, password))
        driver.verify_connectivity()
        print("Driver verify_connectivity: PASS")
        
        with driver.session(database=user) as session:
            cnt = session.run("RETURN 1 as cnt").single()["cnt"]
            print(f"Query test: PASS (val={cnt})")
    except Exception as e:
        print(f"FAILED: {type(e).__name__}: {e}")

if __name__ == "__main__":
    main()
