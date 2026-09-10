import os
from neo4j import GraphDatabase
from dotenv import load_dotenv

load_dotenv("backend/.env")

uri = os.environ.get("NEO4J_URI")
user = os.environ.get("NEO4J_USER")
password = os.environ.get("NEO4J_PASSWORD")

driver = GraphDatabase.driver(uri, auth=(user, password))

def test_gds():
    with driver.session() as session:
        print("Testing GDS...")
        try:
            result = session.run("CALL gds.version() YIELD gdsVersion RETURN gdsVersion")
            version = result.single()
            if version:
                print(f"GDS Version: {version['gdsVersion']}")
            else:
                print("GDS Version returned no results.")
        except Exception as e:
            print(f"GDS Version Error: {e}")

        try:
            result = session.run("CALL dbms.components() YIELD name, versions, edition RETURN name, versions, edition")
            for record in result:
                print(f"DBMS: {record['name']}, Versions: {record['versions']}, Edition: {record['edition']}")
        except Exception as e:
            print(f"DBMS Info Error: {e}")

        try:
            # Just check if louvain procedure exists
            result = session.run("SHOW PROCEDURES YIELD name WHERE name STARTS WITH 'gds.louvain' RETURN name")
            print("Louvain procedures:")
            found = False
            for record in result:
                found = True
                print(f"- {record['name']}")
            if not found:
                print("None found")
        except Exception as e:
            print(f"Show Procedures Error: {e}")

        try:
            # Check db count
            result = session.run("MATCH (n) RETURN count(n) as nodeCount")
            print(f"Total nodes: {result.single()['nodeCount']}")
            
            result = session.run("MATCH ()-[r]->() RETURN count(r) as relCount")
            print(f"Total relationships: {result.single()['relCount']}")
            
            result = session.run("MATCH ()-[r]->() RETURN type(r) as type, count(r) as c")
            print("Relationship types:")
            for record in result:
                print(f"- {record['type']}: {record['c']}")
        except Exception as e:
            print(f"Count Error: {e}")

test_gds()
driver.close()
