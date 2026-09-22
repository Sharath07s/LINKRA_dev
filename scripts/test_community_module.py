#!/usr/bin/env python3
"""
Direct test of the Neo4jCommunityAnalytics.get_communities() method.
This validates the FastAPI-wired module works correctly.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from app.ai.neo4j.community import neo4j_community
import json

print("=" * 60)
print("  Testing neo4j_community.get_communities('louvain')")
print("=" * 60)

result = neo4j_community.get_communities(algorithm="louvain")
print(f"Status: {result.status}")
print(f"Message: {result.message}")
print(f"Algorithm: {result.algorithm}")
print(f"Total communities: {len(result.communities)}")

multi = [c for c in result.communities if c.size > 1]
print(f"Multi-member communities: {len(multi)}")

for c in multi:
    print(f"\n  Community {c.community_id} (size={c.size}):")
    print(f"    Members: {[m.name for m in c.members]}")
    print(f"    Types: {set(m.type for m in c.members)}")
    print(f"    Influential: {c.influential_entity}")
    print(f"    Bridges: {c.bridge_candidates}")
    print(f"    Rel types: {c.relationship_types}")

print("\n" + "=" * 60)
print("  Testing neo4j_community.get_communities('leiden')")
print("=" * 60)

result2 = neo4j_community.get_communities(algorithm="leiden")
print(f"Status: {result2.status}")
print(f"Algorithm: {result2.algorithm}")
multi2 = [c for c in result2.communities if c.size > 1]
print(f"Multi-member communities: {len(multi2)}")

print("\n" + "=" * 60)
print(f"  RESULT: {'✅ PASS' if result.status == 'success' and result2.status == 'success' else '❌ FAIL'}")
print("=" * 60)
