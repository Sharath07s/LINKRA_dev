"""
Test GDS on AuraDB Free — using gds.session.getOrCreate + correct memory format.
"""
import os
from dotenv import load_dotenv
from neo4j import GraphDatabase

def main():
    load_dotenv()
    
    uri = os.getenv("NEO4J_URI")
    user = os.getenv("NEO4J_USER")
    password = os.getenv("NEO4J_PASSWORD")
    
    driver = GraphDatabase.driver(uri, auth=(user, password))
    driver.verify_connectivity()
    print("Connected: PASS\n")
    
    with driver.session(database=user) as session:
        node_count = session.run("MATCH (n) RETURN count(n) AS cnt").single()["cnt"]
        rel_count = session.run("MATCH ()-[r]->() RETURN count(r) AS cnt").single()["cnt"]
        print(f"Graph: {node_count} nodes, {rel_count} relationships")

        # Check session.getOrCreate signature
        print("\n--- gds.session.getOrCreate signature ---")
        try:
            result = session.run(
                "SHOW PROCEDURES YIELD name, signature WHERE name = 'gds.session.getOrCreate' RETURN signature"
            ).single()
            print(f"  {result['signature']}")
        except Exception as e:
            print(f"  FAILED: {e}")

        # Check session.list signature
        print("\n--- gds.session.list signature ---")
        try:
            result = session.run(
                "SHOW PROCEDURES YIELD name, signature WHERE name = 'gds.session.list' RETURN signature"
            ).single()
            print(f"  {result['signature']}")
        except Exception as e:
            print(f"  FAILED: {e}")

        # List existing sessions
        print("\n--- List sessions ---")
        try:
            result = session.run("CALL gds.session.list()")
            for r in result:
                print(f"  Session: {dict(r)}")
        except Exception as e:
            print(f"  FAILED: {e}")

        # Try gds.graph.project with memory param inline (no separate session)
        print("\n--- gds.graph.project with memory='2GB' ---")
        try:
            try:
                session.run("CALL gds.graph.drop('linkra_graph', false)")
            except:
                pass
            
            result = session.run("""
                CALL gds.graph.project(
                    'linkra_graph',
                    '*',
                    '*',
                    {
                        undirectedRelationshipTypes: ['*'],
                        memory: '2GB'
                    }
                )
                YIELD graphName, nodeCount, relationshipCount
                RETURN graphName, nodeCount, relationshipCount
            """).single()
            print(f"  Projected: {result['graphName']} ({result['nodeCount']} nodes, {result['relationshipCount']} rels)")
            
            # Run Louvain
            print("\n--- gds.louvain.stream ---")
            louvain = session.run("""
                CALL gds.louvain.stream('linkra_graph')
                YIELD nodeId, communityId
                RETURN gds.util.asNode(nodeId).name AS entity,
                       labels(gds.util.asNode(nodeId)) AS labels,
                       communityId
                ORDER BY communityId, entity
            """)
            rows = [dict(r) for r in louvain]
            communities = set(r["communityId"] for r in rows)
            print(f"  LOUVAIN: {len(rows)} nodes, {len(communities)} communities")
            for row in rows:
                print(f"    {row['entity']} ({row['labels']}) -> community {row['communityId']}")
            
            # Run Leiden
            print("\n--- gds.leiden.stream ---")
            leiden = session.run("""
                CALL gds.leiden.stream('linkra_graph')
                YIELD nodeId, communityId
                RETURN gds.util.asNode(nodeId).name AS entity,
                       labels(gds.util.asNode(nodeId)) AS labels,
                       communityId
                ORDER BY communityId, entity
            """)
            rows = [dict(r) for r in leiden]
            communities = set(r["communityId"] for r in rows)
            print(f"  LEIDEN: {len(rows)} nodes, {len(communities)} communities")
            for row in rows:
                print(f"    {row['entity']} ({row['labels']}) -> community {row['communityId']}")
            
            # Cleanup
            session.run("CALL gds.graph.drop('linkra_graph', false)")
            print("\nCleanup: PASS")
            
        except Exception as e:
            print(f"  FAILED: {type(e).__name__}: {e}")
    
    driver.close()
    print("\n=== TEST COMPLETE ===")

if __name__ == "__main__":
    main()
