import pytest
from uuid import uuid4
from app.models.resolution import CanonicalEntity
from app.models.ingestion import EntityCandidate
from app.nlp.resolution.engine import resolve_candidate
from app.nlp.resolution.normalization import normalize_entity
from app.nlp.resolution.matching import get_string_similarity

def test_normalization():
    assert normalize_entity("PERSON", "  John   Doe ") == "john doe"
    assert normalize_entity("PHONE", "+91 99887 76655") == "+919988776655"
    assert normalize_entity("VEHICLE", "KA 01 AB 1234") == "KA01AB1234"

def test_string_similarity():
    score = get_string_similarity("john doe", "jon doe")
    assert score > 0.8
    assert score < 1.0

# In a real environment with DB running, we would write an integration test for resolve_candidate
