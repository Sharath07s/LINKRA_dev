"""
Test direct Neo4j connectivity with proper database name.
The Aura Free database name is the instance ID: f725a8a2
"""
import os
from dotenv import load_dotenv
from neo4j import GraphDatabase

def main():
    load_dotenv()

    print("DIRECT NEO4J CONNECTIVITY TEST (ALL SCHEMES)")
    print("=" * 60)

    neo4j_user = os.getenv("NEO4J_USER", os.getenv("NEO4J_USERNAME"))
    neo4j_password = os.getenv("NEO4J_PASSWORD")
    host = "f725a8a2.databases.neo4j.io"
    db_name = neo4j_user  # f725a8a2

    schemes = [
        ("neo4j+ssc", f"neo4j+ssc://{host}"),
        ("neo4j+s", f"neo4j+s://{host}"),
        ("bolt+ssc", f"bolt+ssc://{host}"),
        ("bolt+s", f"bolt+s://{host}"),
    ]

    for scheme_name, uri in schemes:
        print(f"\n--- Testing {scheme_name} (database={db_name}) ---")
        try:
            driver = GraphDatabase.driver(uri, auth=(neo4j_user, neo4j_password))
            driver.verify_connectivity(database=db_name)
            print(f"  verify_connectivity: PASS")
            
            with driver.session(database=db_name) as session:
                result = session.run("RETURN 1 AS val")
                val = result.single()["val"]
                print(f"  RETURN 1: PASS (val={val})")
                
                node_count = session.run("MATCH (n) RETURN count(n) AS cnt").single()["cnt"]
                rel_count = session.run("MATCH ()-[r]->() RETURN count(r) AS cnt").single()["cnt"]
                print(f"  Graph: {node_count} nodes, {rel_count} relationships")
                
                labels = session.run("CALL db.labels() YIELD label RETURN collect(label) AS labels").single()["labels"]
                print(f"  Labels: {labels}")
                
                rel_types = session.run("CALL db.relationshipTypes() YIELD relationshipType RETURN collect(relationshipType) AS types").single()["types"]
                print(f"  Relationship types: {rel_types}")
            
            driver.close()
            print(f"  STATUS: PASS")
        except Exception as e:
            print(f"  STATUS: FAILED ({type(e).__name__}: {e})")
            try:
                driver.close()
            except:
                pass

if __name__ == "__main__":
    main()
