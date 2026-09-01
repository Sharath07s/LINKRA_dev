from typing import List
from sqlalchemy.orm import Session
from sqlalchemy import or_, cast, Text
from app.models.resolution import CanonicalEntity
from app.models.ingestion import EntityCandidate
from app.nlp.resolution.schemas import ResolutionContext

def find_candidates(db: Session, candidate: EntityCandidate, context: ResolutionContext) -> List[CanonicalEntity]:
    """
    Finds potential CanonicalEntity matches for a given EntityCandidate.
    Uses blocking keys like exact normalized value, phones, and vehicles to bound O(N^2) complexity.
    """
    if not candidate.normalized_value:
        return []

    # 1. Look for entities of the same type
    query = db.query(CanonicalEntity).filter(CanonicalEntity.entity_type == candidate.entity_type)
    
    # 2. Add filters based on type
    if candidate.entity_type in ["PHONE", "VEHICLE", "ACCOUNT"]:
        # Needs exact matches on normalized value
        query = query.filter(CanonicalEntity.name == candidate.normalized_value)
    else:
        search_term = candidate.normalized_value
        prefix = search_term[:3] if len(search_term) >= 3 else search_term
        
        # Build blocking clauses
        clauses = [
            CanonicalEntity.name.ilike(f"{prefix}%"),
            cast(CanonicalEntity.aliases, Text).ilike(f"%{search_term}%")
        ]
        
        # If we have strong context (phone/vehicle), use it as a blocking key
        for p in context.phones:
            clauses.append(cast(CanonicalEntity.attributes, Text).ilike(f"%{p}%"))
        for v in context.vehicles:
            clauses.append(cast(CanonicalEntity.attributes, Text).ilike(f"%{v}%"))
            
        query = query.filter(or_(*clauses))
        
    return query.all()
