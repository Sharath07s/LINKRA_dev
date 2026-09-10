"""
Direct Neo4j Connectivity Test
------------------------------
"""
import os
import sys
from dotenv import load_dotenv
from neo4j import GraphDatabase

def main():
    load_dotenv()

    print("DIRECT NEO4J CONNECTIVITY TEST")
    print("------------------------------")

    neo4j_uri = os.getenv("NEO4J_URI").replace("neo4j+ssc://", "neo4j+s://")
    neo4j_user = os.getenv("NEO4J_USER", os.getenv("NEO4J_USERNAME"))
    neo4j_password = os.getenv("NEO4J_PASSWORD")
    neo4j_database = os.getenv("NEO4J_DATABASE", "LINKRA_DB")

    missing = []
    if not neo4j_uri:
        missing.append("NEO4J_URI")
    if not neo4j_user:
        missing.append("NEO4J_USER")
    if not neo4j_password:
        missing.append("NEO4J_PASSWORD")

    if missing:
        print(f"Environment: FAILED (Missing: {', '.join(missing)})")
        return
    print(f"Environment: PASS (URI scheme: {neo4j_uri.split('://')[0]}, Database: {neo4j_database})")

    try:
        driver = GraphDatabase.driver(neo4j_uri, auth=(neo4j_user, neo4j_password))
        print("Driver creation: PASS")
    except Exception as e:
        print(f"Driver creation: FAILED ({type(e).__name__}: {e})")
        return

    try:
        with driver.session() as session:
            # Show databases
            dbs = session.run("SHOW DATABASES YIELD name, currentStatus").data()
            print(f"Available databases: {dbs}")
            
            # If neo4j database exists, try it
            result = session.run("RETURN 1 AS val")
            val = result.single()["val"]
            print(f"RETURN 1: PASS (val={val})")

            # 9. Simple graph query
            labels = session.run("CALL db.labels() YIELD label RETURN collect(label) AS labels").single()["labels"]
            print(f"Labels: {labels}")

    except Exception as e:
        print(f"Query execution: FAILED ({type(e).__name__}: {e})")
    finally:
        driver.close()

if __name__ == "__main__":
    main()
