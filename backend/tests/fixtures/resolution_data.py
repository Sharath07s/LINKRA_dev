from app.models.ingestion import EntityCandidate
from app.models.resolution import CanonicalEntity
from app.nlp.resolution.schemas import ResolutionContext

def get_test_candidate_ravi():
    return EntityCandidate(
        id="11111111-1111-1111-1111-111111111111",
        entity_type="PERSON",
        raw_text="Ravi Kumar",
        normalized_value="Ravi Kumar",
        confidence=0.9
    )

def get_test_canonical_ravi():
    return CanonicalEntity(
        id="22222222-2222-2222-2222-222222222222",
        entity_type="PERSON",
        name="Ravi Kumar",
        aliases=[],
        attributes={
            "phones": ["9876543210"],
            "locations": ["Bengaluru"]
        }
    )

def get_test_canonical_ravi_diff_phone():
    return CanonicalEntity(
        id="33333333-3333-3333-3333-333333333333",
        entity_type="PERSON",
        name="Ravi Kumar",
        aliases=[],
        attributes={
            "phones": ["9988776655"]
        }
    )
