import difflib
from typing import Dict, Any, List
from app.models.resolution import CanonicalEntity
from app.models.ingestion import EntityCandidate
from app.nlp.resolution.schemas import ResolutionContext
from app.core.config import settings

def get_string_similarity(a: str, b: str) -> float:
    """Returns a float between 0.0 and 1.0 representing string similarity using difflib."""
    if not a or not b:
        return 0.0
    return difflib.SequenceMatcher(None, a.lower(), b.lower()).ratio()

def check_overlap(list1: List[str], list2: List[str]) -> bool:
    if not list1 or not list2:
        return False
    return bool(set(list1) & set(list2))

def check_mismatch(list1: List[str], list2: List[str]) -> bool:
    if not list1 or not list2:
        return False
    return not bool(set(list1) & set(list2))

def score_match(candidate: EntityCandidate, context: ResolutionContext, canonical: CanonicalEntity) -> Dict[str, Any]:
    """
    Compares an EntityCandidate to a CanonicalEntity and returns a detailed scoring payload.
    """
    score_details = {
        "score": 0.0,
        "decision": "UNRESOLVED",
        "veto": False,
        "signals": {
            "name_similarity": 0.0,
            "phone_match": 0.0,
            "vehicle_match": 0.0,
            "location_match": 0.0,
            "temporal_penalty": 0.0
        },
        "reason": ""
    }
    
    cand_val = candidate.normalized_value or ""
    can_val = canonical.name or ""
    
    # Entity Type Check
    if candidate.entity_type != canonical.entity_type:
        score_details["veto"] = True
        score_details["reason"] += "Entity type mismatch. "
        score_details["decision"] = "REVIEW_REQUIRED"
        return score_details
        
    # Fast path for explicit exact-match entities
    if candidate.entity_type in ["PHONE", "VEHICLE", "ACCOUNT"]:
        if cand_val == can_val:
            score_details["score"] = 1.0
            score_details["signals"]["name_similarity"] = 1.0
            score_details["decision"] = "AUTO_MATCHED"
            score_details["reason"] = f"Exact {candidate.entity_type} match."
        else:
            score_details["decision"] = "CREATE_NEW"
            score_details["reason"] = f"Mismatched {candidate.entity_type}."
        return score_details
    
    # Name Similarity (applies to PERSON, ORG, LOC, DATE, EVENT)
    if cand_val == can_val or cand_val in (canonical.aliases or []):
        score_details["signals"]["name_similarity"] = 1.0
    else:
        sim1 = get_string_similarity(cand_val, can_val)
        sim2 = 0.0
        for alias in (canonical.aliases or []):
            sim_alias = get_string_similarity(cand_val, alias)
            if sim_alias > sim2:
                sim2 = sim_alias
        score_details["signals"]["name_similarity"] = max(sim1, sim2)

    attributes = canonical.attributes or {}
    
    # Phone matching
    canonical_phones = attributes.get("phones", [])
    if check_overlap(context.phones, canonical_phones):
        score_details["signals"]["phone_match"] = 1.0
    elif check_mismatch(context.phones, canonical_phones):
        score_details["veto"] = True
        score_details["reason"] += "Explicit phone mismatch. "

    # Vehicle matching
    canonical_vehicles = attributes.get("vehicles", [])
    if check_overlap(context.vehicles, canonical_vehicles):
        score_details["signals"]["vehicle_match"] = 1.0
    elif check_mismatch(context.vehicles, canonical_vehicles):
        score_details["veto"] = True
        score_details["reason"] += "Explicit vehicle mismatch. "
        
    # Location matching (fuzzy or exact)
    canonical_locations = attributes.get("locations", [])
    if check_overlap(context.locations, canonical_locations):
        score_details["signals"]["location_match"] = 1.0
        
    # Calculate score
    base_score = (
        (score_details["signals"]["name_similarity"] * settings.RESOLUTION_WEIGHT_NAME) +
        (score_details["signals"]["phone_match"] * settings.RESOLUTION_WEIGHT_PHONE) +
        (score_details["signals"]["vehicle_match"] * settings.RESOLUTION_WEIGHT_VEHICLE) +
        (score_details["signals"]["location_match"] * settings.RESOLUTION_WEIGHT_LOCATION)
    )
    
    # Temporal penalty
    canonical_dates = attributes.get("dates", [])
    if check_mismatch(context.dates, canonical_dates):
        score_details["signals"]["temporal_penalty"] = settings.RESOLUTION_TEMPORAL_PENALTY
        base_score -= settings.RESOLUTION_TEMPORAL_PENALTY
        score_details["reason"] += "Temporal penalty applied. "
        
    score_details["score"] = max(0.0, base_score)
    
    # Decisions
    if score_details["veto"]:
        score_details["decision"] = "REVIEW_REQUIRED"
    elif score_details["score"] >= settings.RESOLUTION_THRESHOLD_AUTO_MATCH:
        score_details["decision"] = "AUTO_MATCHED"
        score_details["reason"] += "High confidence match."
    elif score_details["score"] >= settings.RESOLUTION_THRESHOLD_REVIEW:
        score_details["decision"] = "REVIEW_REQUIRED"
        score_details["reason"] += "Medium confidence match requires review."
    else:
        score_details["decision"] = "CREATE_NEW"
        score_details["reason"] += "Low confidence, creating new entity."
        
    return score_details
