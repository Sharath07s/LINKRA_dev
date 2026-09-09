import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app.db.session import SessionLocal
from app.nlp.llm_extractor import extract_entities_llm
from app.nlp.resolution.engine import resolve_candidate
from app.nlp.resolution.schemas import ResolutionContext

def test_pipeline():
    db = SessionLocal()
    
    text = "On 2023-01-15, Officer John Doe (Phone: 555-9999) investigated a suspect named Jane Smith driving a blue Toyota with license XYZ-123. Jane Smith is associated with the 5th Street Gang."
    
    print("1. Extracting entities via LLM...")
    candidates = extract_entities_llm(text)
    print(f"Extracted {len(candidates)} entities.")
    
    print("2. Resolving candidates...")
    context = ResolutionContext()
    for c in candidates:
        print(f"   -> Resolving {c.raw_text} ({c.entity_type})")
        status, canonical_id, score, evidence = resolve_candidate(db, c, context)
        c.resolved_to_id = canonical_id
        print(f"      Resolved to {canonical_id} with status {status}")
        
    print("3. Extracting relationships via LLM...")
    from app.nlp.relationship.extractor import _extract_unstructured
    from app.models.ingestion import IngestionJob
    from app.ingestion.parsers import ParsedPage
    
    job = IngestionJob(id="00000000-0000-0000-0000-000000000000")
    page = ParsedPage(page_number=1, text=text, metadata={})
    
    rels = _extract_unstructured(job, page, candidates)
    print(f"Extracted {len(rels)} relationships.")
    for r in rels:
        print(f" - {r.source_entity_id} {r.relationship_type} {r.target_entity_id}")

if __name__ == "__main__":
    test_pipeline()
