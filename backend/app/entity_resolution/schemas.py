from pydantic import BaseModel

class ResolutionDecision(BaseModel):
    # PLACEHOLDER
    extracted_entity_id: str
    canonical_entity_id: str
    similarity_score: float
