import uuid
import logging
from typing import Optional, Tuple
from sqlalchemy.orm import Session

from app.models.resolution import CanonicalEntity
from app.models.ingestion import EntityCandidate
from app.nlp.resolution.schemas import ResolutionContext
from app.nlp.resolution.candidate_generation import find_candidates
from app.nlp.resolution.matching import score_match
from app.ai.neo4j.intelligence import neo4j_intelligence

logger = logging.getLogger(__name__)

def resolve_candidate(db: Session, candidate: EntityCandidate, context: ResolutionContext) -> Tuple[str, Optional[uuid.UUID], float, dict]:
    """
    Attempts to resolve an EntityCandidate to a CanonicalEntity.
    Returns: (resolution_status, canonical_entity_id, resolution_score, resolution_evidence)
    """
    candidates = find_candidates(db, candidate, context)
    
    if not candidates:
        return create_new_canonical(db, candidate, context)

    best_candidate = None
    best_details = None
    best_score = -1.0
    
    for can in candidates:
        details = score_match(candidate, context, can)
        
        # We always want the match with the highest valid score, 
        # but if we get a veto (REVIEW_REQUIRED), we should still consider its score 
        # for ranking among other potential matches.
        if details["score"] > best_score:
            best_score = details["score"]
            best_candidate = can
            best_details = details

    if not best_candidate or not best_details:
        return create_new_canonical(db, candidate, context)

    # Process final decision
    decision = best_details["decision"]
    if decision == "CREATE_NEW":
        return create_new_canonical(db, candidate, context, best_details)
        
    elif decision == "AUTO_MATCHED":
        _merge_attributes(best_candidate, context)
        db.add(best_candidate)
        db.commit()
        db.refresh(best_candidate)
        
        # Sync to Neo4j on update
        neo4j_intelligence.sync_canonical_entity(
            entity_id=str(best_candidate.id),
            entity_type=best_candidate.entity_type,
            properties={
                "name": best_candidate.name,
                "aliases": best_candidate.aliases
            }
        )
        return (decision, best_candidate.id, best_score, best_details)
        
    else:
        # REVIEW_REQUIRED
        return (decision, best_candidate.id, best_score, best_details)


def create_new_canonical(db: Session, candidate: EntityCandidate, context: ResolutionContext, evidence: dict = None) -> Tuple[str, uuid.UUID, float, dict]:
    """Creates a new canonical entity from a candidate."""
    if evidence is None:
        evidence = {
            "score": 0.0,
            "decision": "CREATE_NEW",
            "veto": False,
            "signals": {},
            "reason": "No matches found."
        }
        
    canonical = CanonicalEntity(
        entity_type=candidate.entity_type,
        name=candidate.normalized_value or candidate.raw_text,
        aliases=[candidate.raw_text] if candidate.raw_text != candidate.normalized_value else [],
        attributes={}
    )
    
    _merge_attributes(canonical, context)
    
    db.add(canonical)
    db.commit()
    db.refresh(canonical)
    
    # Sync to Neo4j
    neo4j_intelligence.sync_canonical_entity(
        entity_id=str(canonical.id),
        entity_type=canonical.entity_type,
        properties={
            "name": canonical.name,
            "aliases": canonical.aliases
        }
    )
    
    return ("AUTO_MATCHED", canonical.id, 1.0, evidence)


def _merge_attributes(canonical: CanonicalEntity, context: ResolutionContext):
    """Safely merges context values into the canonical entity's attributes."""
    # Ensure attributes is a dict
    if canonical.attributes is None:
        canonical.attributes = {}
        
    # We must explicitly re-assign to trigger SQLAlchemy JSON mutation detection,
    # or use sqlalchemy.ext.mutable. For safety, re-assign a new dict.
    new_attrs = dict(canonical.attributes)
    
    def merge_list(key, new_items):
        if not new_items:
            return
        existing = new_attrs.get(key, [])
        for item in new_items:
            if item not in existing:
                existing.append(item)
        new_attrs[key] = existing

    merge_list("phones", context.phones)
    merge_list("vehicles", context.vehicles)
    merge_list("locations", context.locations)
    merge_list("organizations", context.organizations)
    merge_list("dates", context.dates)
    
    canonical.attributes = new_attrs
