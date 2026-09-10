"""
LINKRA GDS Session Test — Fixed for self-signed certificate on Aura Free.

ROOT CAUSE: The AuraDB Free instance uses a self-signed TLS certificate.
The graphdatascience library internally uses neo4j+s:// (verified TLS)
which fails certificate verification. The fix is to:
1. Provide URI directly as neo4j+ssc:// (skip cert verification)
2. NOT use aura_instance_id (which forces neo4j+s:// from the API)
"""
import os
import sys
from datetime import timedelta
from dotenv import load_dotenv


def main():
    load_dotenv()

    print("LINKRA GDS SESSION TEST (Self-Signed Cert Fix)")
    print("=" * 55)

    # ── 1. Environment ──────────────────────────────────────
    client_id = os.getenv("AURA_CLIENT_ID")
    client_secret = os.getenv("AURA_CLIENT_SECRET")
    neo4j_uri = os.getenv("NEO4J_URI")  # neo4j+ssc://f725a8a2.databases.neo4j.io
    neo4j_user = os.getenv("NEO4J_USER", os.getenv("NEO4J_USERNAME"))
    neo4j_password = os.getenv("NEO4J_PASSWORD")

    missing = []
    if not client_id:     missing.append("AURA_CLIENT_ID")
    if not client_secret: missing.append("AURA_CLIENT_SECRET")
    if not neo4j_uri:     missing.append("NEO4J_URI")
    if not neo4j_user:    missing.append("NEO4J_USER")
    if not neo4j_password: missing.append("NEO4J_PASSWORD")

    if missing:
        print(f"Environment: FAILED (Missing: {', '.join(missing)})")
        return
    print(f"Environment: PASS")

    # ── 2. Aura API authentication ──────────────────────────
    from graphdatascience import GdsSessions
    from graphdatascience.session import (
        AuraAPICredentials,
        DbmsConnectionInfo,
        SessionMemory,
    )

    credentials = AuraAPICredentials(client_id=client_id, client_secret=client_secret)
    sessions_mgr = GdsSessions(api_credentials=credentials)
    print("Aura API Auth: PASS")

    # ── 3. Clean stale sessions ─────────────────────────────
    existing = sessions_mgr.list()
    if existing:
        print(f"  Found {len(existing)} existing session(s)")
        for s in existing:
            print(f"    {s.name} (status={s.status})")
            if s.status.lower() in ("ready", "creating", "starting"):
                print(f"    Deleting stale session '{s.name}'...")
                sessions_mgr.delete(session_name=s.name)
                print(f"    Deleted.")

    # ── 4. Create GDS session ───────────────────────────────
    # KEY FIX: Use neo4j+ssc:// URI directly (NOT aura_instance_id)
    # because Aura Free has self-signed cert that neo4j+s:// rejects.
    # The database name on Aura Free = the instance ID (f725a8a2).
    db_connection = DbmsConnectionInfo(
        uri=neo4j_uri,  # neo4j+ssc://f725a8a2.databases.neo4j.io
        username=neo4j_user,
        password=neo4j_password,
        database=neo4j_user,  # f725a8a2
    )

    session = None
    try:
        session = sessions_mgr.get_or_create(
            session_name="linkra-gds-m14",
            memory=SessionMemory.m_2GB,
            db_connection=db_connection,
            ttl=timedelta(minutes=30),
        )
        print("GDS Session: PASS")
    except Exception as e:
        print(f"GDS Session: FAILED ({type(e).__name__}: {e})")
        return

    # ── 5. Verify GDS connectivity ──────────────────────────
    try:
        # run_cypher verifies the session is usable
        result = session.run_cypher("RETURN 1 AS val")
        val = result["val"].iloc[0]
        print(f"GDS Connectivity: PASS (val={val})")
    except Exception as e:
        print(f"GDS Connectivity: FAILED ({type(e).__name__}: {e})")

    # ── 6. Inspect LINKRA graph ─────────────────────────────
    try:
        node_result = session.run_cypher("MATCH (n) RETURN count(n) AS cnt")
        rel_result = session.run_cypher("MATCH ()-[r]->() RETURN count(r) AS cnt")
        node_count = node_result["cnt"].iloc[0]
        rel_count = rel_result["cnt"].iloc[0]
        print(f"LINKRA Graph: {node_count} nodes, {rel_count} relationships")

        labels_result = session.run_cypher("CALL db.labels() YIELD label RETURN collect(label) AS labels")
        print(f"Labels: {labels_result['labels'].iloc[0]}")

        rel_types_result = session.run_cypher("CALL db.relationshipTypes() YIELD relationshipType RETURN collect(relationshipType) AS types")
        print(f"Rel Types: {rel_types_result['types'].iloc[0]}")
    except Exception as e:
        print(f"Graph Inspection: FAILED ({type(e).__name__}: {e})")

    # ── 7. Test GDS graph projection ────────────────────────
    try:
        # Drop existing projection if any
        try:
            session.run_cypher("CALL gds.graph.drop('linkra_community_graph', false)")
        except:
            pass

        # Project the graph
        proj_result = session.run_cypher("""
            CALL gds.graph.project(
                'linkra_community_graph',
                '*',
                {
                    ALL: {
                        type: '*',
                        orientation: 'UNDIRECTED'
                    }
                }
            )
        """)
        print(f"Graph Projection: PASS")
        print(f"  Projected nodes: {proj_result.get('nodeCount', ['?']).iloc[0] if 'nodeCount' in proj_result.columns else '?'}")
        print(f"  Projected rels: {proj_result.get('relationshipCount', ['?']).iloc[0] if 'relationshipCount' in proj_result.columns else '?'}")
    except Exception as e:
        print(f"Graph Projection: FAILED ({type(e).__name__}: {e})")

    # ── 8. Execute LOUVAIN ──────────────────────────────────
    try:
        louvain_result = session.run_cypher("""
            CALL gds.louvain.stream('linkra_community_graph')
            YIELD nodeId, communityId
            RETURN gds.util.asNode(nodeId).name AS entity,
                   labels(gds.util.asNode(nodeId)) AS labels,
                   communityId
            ORDER BY communityId, entity
        """)
        num_communities = louvain_result["communityId"].nunique()
        print(f"Louvain: PASS ({len(louvain_result)} nodes, {num_communities} communities)")
        print(f"  Communities: {louvain_result.groupby('communityId').size().to_dict()}")
    except Exception as e:
        print(f"Louvain: FAILED ({type(e).__name__}: {e})")

    # ── 9. Execute LEIDEN ───────────────────────────────────
    try:
        leiden_result = session.run_cypher("""
            CALL gds.leiden.stream('linkra_community_graph')
            YIELD nodeId, communityId
            RETURN gds.util.asNode(nodeId).name AS entity,
                   labels(gds.util.asNode(nodeId)) AS labels,
                   communityId
            ORDER BY communityId, entity
        """)
        num_communities = leiden_result["communityId"].nunique()
        print(f"Leiden: PASS ({len(leiden_result)} nodes, {num_communities} communities)")
        print(f"  Communities: {leiden_result.groupby('communityId').size().to_dict()}")
    except Exception as e:
        print(f"Leiden: FAILED ({type(e).__name__}: {e})")

    # ── 10. Cleanup ─────────────────────────────────────────
    try:
        session.run_cypher("CALL gds.graph.drop('linkra_community_graph', false)")
        print("Graph projection cleanup: PASS")
    except Exception as e:
        print(f"Graph projection cleanup: WARNING ({e})")

    # Don't delete session yet — we may need it for integration
    print(f"\nSession ID: {session._session_lifecycle_manager._session_id if hasattr(session, '_session_lifecycle_manager') else 'unknown'}")
    print("Session left running for integration testing.")
    print("\n" + "=" * 55)
    print("TEST COMPLETE")


if __name__ == "__main__":
    main()
