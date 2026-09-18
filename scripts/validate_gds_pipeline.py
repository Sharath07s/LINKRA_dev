#!/usr/bin/env python3
"""
LINKRA — Full GDS Community Detection Pipeline Validation
Runs Louvain + Leiden against the REAL 140-node graph in local Neo4j.

This is the PROOF script: if this passes, the pipeline is live.
"""
from neo4j import GraphDatabase
from collections import defaultdict
import json

URI   = "bolt://localhost:7687"
USER  = "neo4j"
PASS  = "linkra2024"
PROJ  = "linkra_pipeline_validation"

driver = GraphDatabase.driver(URI, auth=(USER, PASS))

def header(s):
    print(f"\n{'='*60}")
    print(f"  {s}")
    print(f"{'='*60}")

# ── Step 1: Verify GDS is available ──
header("STEP 1 — GDS Availability")
with driver.session() as s:
    v = s.run("RETURN gds.version() AS v").single()["v"]
    print(f"  GDS version: {v}")

# ── Step 2: Verify graph data ──
header("STEP 2 — Graph Data in Neo4j")
with driver.session() as s:
    nodes = s.run("MATCH (n) RETURN count(n) AS c").single()["c"]
    rels  = s.run("MATCH ()-[r]->() RETURN count(r) AS c").single()["c"]
    labels = [r["label"] for r in s.run("CALL db.labels() YIELD label RETURN label")]
    rel_types = [r["relationshipType"] for r in s.run("CALL db.relationshipTypes() YIELD relationshipType RETURN relationshipType")]
    print(f"  Nodes: {nodes}")
    print(f"  Relationships: {rels}")
    print(f"  Labels: {labels}")
    print(f"  Relationship types: {rel_types}")

if nodes == 0:
    print("\n❌ FATAL: Zero nodes in Neo4j — cannot run community detection.")
    exit(1)

# ── Step 3: Project graph + run Louvain ──
header("STEP 3 — GDS Projection + Louvain")
with driver.session() as s:
    # Drop if exists
    try:
        s.run(f"CALL gds.graph.drop('{PROJ}', false)")
    except:
        pass

    # Project — use undirected for community detection
    proj_result = s.run(f"""
        CALL gds.graph.project(
            '{PROJ}',
            '*',
            {{
                _ALL_: {{
                    type: '*',
                    orientation: 'UNDIRECTED'
                }}
            }}
        )
        YIELD graphName, nodeCount, relationshipCount
        RETURN graphName, nodeCount, relationshipCount
    """).single()
    print(f"  Projected: {proj_result['graphName']}")
    print(f"  Nodes in projection: {proj_result['nodeCount']}")
    print(f"  Rels in projection: {proj_result['relationshipCount']}")

    # Run Louvain
    print("\n  Running Louvain...")
    louvain_rows = []
    result = s.run(f"""
        CALL gds.louvain.stream('{PROJ}')
        YIELD nodeId, communityId
        RETURN gds.util.asNode(nodeId).id AS entity_id,
               gds.util.asNode(nodeId).name AS name,
               gds.util.asNode(nodeId).entity_type AS entity_type,
               communityId
        ORDER BY communityId, entity_id
    """)
    for r in result:
        louvain_rows.append(dict(r))
    
    print(f"  Louvain returned {len(louvain_rows)} rows")
    
    # Group by community
    louvain_communities = defaultdict(list)
    for row in louvain_rows:
        louvain_communities[row["communityId"]].append(row)
    
    multi_member = {k: v for k, v in louvain_communities.items() if len(v) > 1}
    singletons = {k: v for k, v in louvain_communities.items() if len(v) == 1}
    
    print(f"  Total communities: {len(louvain_communities)}")
    print(f"  Multi-member communities: {len(multi_member)}")
    print(f"  Singletons: {len(singletons)}")
    
    print("\n  === REAL Louvain Communities (multi-member) ===")
    for cid, members in sorted(multi_member.items(), key=lambda x: -len(x[1])):
        names = [m["name"] or "?" for m in members]
        types = set(m["entity_type"] or "?" for m in members)
        print(f"  Community {cid} ({len(members)} members, types: {types}):")
        for name in names[:10]:
            print(f"    - {name}")
        if len(names) > 10:
            print(f"    ... and {len(names)-10} more")

# ── Step 4: Run Leiden ──
header("STEP 4 — Leiden")
with driver.session() as s:
    print("  Running Leiden...")
    leiden_rows = []
    result = s.run(f"""
        CALL gds.leiden.stream('{PROJ}')
        YIELD nodeId, communityId
        RETURN gds.util.asNode(nodeId).id AS entity_id,
               gds.util.asNode(nodeId).name AS name,
               gds.util.asNode(nodeId).entity_type AS entity_type,
               communityId
        ORDER BY communityId, entity_id
    """)
    for r in result:
        leiden_rows.append(dict(r))
    
    leiden_communities = defaultdict(list)
    for row in leiden_rows:
        leiden_communities[row["communityId"]].append(row)
    
    leiden_multi = {k: v for k, v in leiden_communities.items() if len(v) > 1}
    
    print(f"  Leiden returned {len(leiden_rows)} rows")
    print(f"  Total communities: {len(leiden_communities)}")
    print(f"  Multi-member communities: {len(leiden_multi)}")
    
    print("\n  === REAL Leiden Communities (multi-member) ===")
    for cid, members in sorted(leiden_multi.items(), key=lambda x: -len(x[1])):
        names = [m["name"] or "?" for m in members]
        types = set(m["entity_type"] or "?" for m in members)
        print(f"  Community {cid} ({len(members)} members, types: {types}):")
        for name in names[:10]:
            print(f"    - {name}")
        if len(names) > 10:
            print(f"    ... and {len(names)-10} more")

# ── Step 5: Bridge Candidates ──
header("STEP 5 — Bridge Candidates (inter-community connectors)")
with driver.session() as s:
    # Use louvain community assignments
    node_community = {row["entity_id"]: row["communityId"] for row in louvain_rows if row["entity_id"]}
    
    # Find nodes with connections to other communities
    bridge_query = """
    MATCH (n:Entity)-[r]-(m:Entity)
    WHERE n.id <> m.id
    RETURN n.id AS src, n.name AS src_name, m.id AS tgt, m.name AS tgt_name, type(r) AS rel_type
    """
    rels_result = s.run(bridge_query)
    bridges = defaultdict(set)
    for rec in rels_result:
        src_c = node_community.get(rec["src"])
        tgt_c = node_community.get(rec["tgt"])
        if src_c is not None and tgt_c is not None and src_c != tgt_c:
            bridges[rec["src"]].add(rec["tgt"])
    
    if bridges:
        print("  Entities connecting different communities:")
        for eid, targets in sorted(bridges.items(), key=lambda x: -len(x[1]))[:10]:
            src_name = next((r["name"] for r in louvain_rows if r["entity_id"] == eid), eid)
            print(f"    {src_name} (community {node_community.get(eid)}) → connected to {len(targets)} nodes in other communities")
    else:
        print("  No inter-community bridges found (graph may be fully disconnected components)")

# ── Step 6: Structural Influence ──
header("STEP 6 — Structural Influence (Degree within community)")
with driver.session() as s:
    deg_result = s.run("""
        MATCH (n:Entity)-[r]-(m:Entity)
        RETURN n.id AS eid, n.name AS name, count(r) AS degree
        ORDER BY degree DESC
        LIMIT 15
    """)
    print("  Top 15 most connected entities:")
    for rec in deg_result:
        c = node_community.get(rec["eid"], "?")
        print(f"    {rec['name']:30s} degree={rec['degree']:3d}  community={c}")

# ── Step 7: Cleanup ──
header("STEP 7 — Cleanup")
with driver.session() as s:
    s.run(f"CALL gds.graph.drop('{PROJ}', false)")
    print("  Projection dropped.")

driver.close()

# ── FINAL VERDICT ──
header("PIPELINE VALIDATION VERDICT")
checks = {
    "GDS Available": True,
    f"Graph Data ({nodes} nodes, {rels} rels)": nodes > 0 and rels > 0,
    f"Louvain Executed ({len(louvain_rows)} rows, {len(louvain_communities)} communities)": len(louvain_rows) == nodes,
    f"Leiden Executed ({len(leiden_rows)} rows, {len(leiden_communities)} communities)": len(leiden_rows) == nodes,
    "Multi-member communities exist": len(multi_member) > 0,
    "Bridge candidates computed": True,
}

all_pass = True
for check, passed in checks.items():
    status = "✅ PASS" if passed else "❌ FAIL"
    if not passed:
        all_pass = False
    print(f"  {status}: {check}")

print()
if all_pass:
    print("  ✅✅✅ ALL CHECKS PASSED — PIPELINE IS LIVE ✅✅✅")
else:
    print("  ❌ SOME CHECKS FAILED — SEE ABOVE")
