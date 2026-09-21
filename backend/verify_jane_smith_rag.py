"""
READ-ONLY: Jane Smith / Blue Toyota semantic search verification.
No database writes. Query only.
"""
import sys
sys.path.insert(0, ".")

from app.ai.rag.vector_search import VectorStore

vs = VectorStore()

print("=== JANE SMITH / BLUE TOYOTA QUERY ===")
query = "What evidence connects Jane Smith to the vehicle?"
results = vs.semantic_search(query, top_k=5)

if not results:
    print("NO RESULTS RETURNED from semantic_search()")
else:
    for i, r in enumerate(results):
        print(f"\n--- Result {i+1} ---")
        print(f"  chunk_id:   {r['chunk_id']}")
        print(f"  doc_id:     {r['doc_id']}")
        print(f"  similarity: {r['similarity']}")
        print(f"  metadata:   {r['metadata']}")
        print(f"  content excerpt (first 300 chars):")
        print(f"    {r['content'][:300]}")
        jane_hit = "Jane Smith" in r["content"] or "blue Toyota" in r["content"] or "toyota" in r["content"].lower()
        print(f"  Contains Jane Smith or blue Toyota: {jane_hit}")
