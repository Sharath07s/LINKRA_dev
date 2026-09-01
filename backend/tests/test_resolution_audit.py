import pytest
from uuid import uuid4
from sqlalchemy.orm import Session
from app.models.resolution import CanonicalEntity
from app.models.ingestion import EntityCandidate
from app.nlp.resolution.engine import resolve_candidate
from app.nlp.resolution.schemas import ResolutionContext
from app.nlp.resolution.candidate_generation import find_candidates
from app.nlp.resolution.matching import get_string_similarity

def test_fuzzy_matching_string():
    # Case A: Exact same
    assert get_string_similarity("ravi kumar", "ravi kumar") == 1.0
    
    # Case C/F: Similar but different
    # ravi kumar vs raju kumar
    assert get_string_similarity("ravi kumar", "raju kumar") < 0.95
    
    # ravi kumar vs ravi kumarr (typo)
    assert get_string_similarity("ravi kumar", "ravi kumarr") >= 0.95

# We mock DB for testing find_candidates and resolve_candidate
class MockQuery:
    def __init__(self, entities):
        self.entities = entities
    def filter(self, *args, **kwargs):
        return self
    def all(self):
        return self.entities

class MockDB:
    def __init__(self):
        self.entities = []
        self.added = []
        self.committed = False
        self.refreshed = []
    def query(self, model):
        # Return a MockQuery with entities of that type
        return MockQuery(self.entities)
    def add(self, obj):
        if not hasattr(obj, 'id'):
            obj.id = uuid4()
        self.added.append(obj)
    def commit(self):
        self.committed = True
    def refresh(self, obj):
        self.refreshed.append(obj)

# Mock Neo4j
class MockNeo4j:
    def __init__(self):
        self.synced = []
    def sync_canonical_entity(self, entity_id, entity_type, properties):
        self.synced.append((entity_id, entity_type, properties))

import app.nlp.resolution.engine as engine
engine.neo4j_intelligence = MockNeo4j()

def test_engine_exact_match(monkeypatch):
    db = MockDB()
    existing = CanonicalEntity(id=uuid4(), entity_type="PERSON", name="ravi kumar", aliases=[])
    db.entities.append(existing)
    
    candidate = EntityCandidate(
        id=uuid4(),
        entity_type="PERSON",
        raw_text="Ravi Kumar",
        normalized_value="ravi kumar"
    )
    
    # Case A: Exact Match Name Only -> Creates new due to < 0.65 threshold (Name maxes at 0.5)
    status, can_id, score, evidence = resolve_candidate(db, candidate, ResolutionContext())
    assert status == "AUTO_MATCHED"
    assert can_id != existing.id
    assert len(db.added) == 1

def test_engine_fuzzy_typo():
    db = MockDB()
    existing = CanonicalEntity(id=uuid4(), entity_type="PERSON", name="ravi kumar", aliases=[])
    db.entities.append(existing)
    
    candidate = EntityCandidate(
        id=uuid4(),
        entity_type="PERSON",
        raw_text="Ravi Kumarr",
        normalized_value="ravi kumarr"
    )
    
    # Case H: Ambiguous candidate (typo -> Create New due to < 0.65)
    status, can_id, score, evidence = resolve_candidate(db, candidate, ResolutionContext())
    assert status == "AUTO_MATCHED"
    assert can_id != existing.id
    assert len(db.added) == 1

def test_engine_different_name():
    db = MockDB()
    existing = CanonicalEntity(id=uuid4(), entity_type="PERSON", name="ravi kumar", aliases=[])
    db.entities.append(existing)
    
    candidate = EntityCandidate(
        id=uuid4(),
        entity_type="PERSON",
        raw_text="Amit Singh",
        normalized_value="amit singh"
    )
    
    # Case C: Similar but different / low confidence -> Create new
    status, can_id, score, evidence = resolve_candidate(db, candidate, ResolutionContext())
    assert status == "AUTO_MATCHED" # Creates new canonical and auto-matches to it
    assert can_id != existing.id
    assert len(db.added) == 1
    assert db.added[0].name == "amit singh"

def test_engine_phone_exact():
    db = MockDB()
    existing = CanonicalEntity(id=uuid4(), entity_type="PHONE", name="+919988776655", aliases=[])
    db.entities.append(existing)
    
    candidate = EntityCandidate(
        id=uuid4(),
        entity_type="PHONE",
        raw_text="+91 99887 76655",
        normalized_value="+919988776655"
    )
    
    status, can_id, score, evidence = resolve_candidate(db, candidate, ResolutionContext())
    assert status == "AUTO_MATCHED"
    assert can_id == existing.id
    assert score == 1.0

def test_engine_phone_different():
    db = MockDB()
    existing = CanonicalEntity(id=uuid4(), entity_type="PHONE", name="+919988776655", aliases=[])
    db.entities.append(existing)
    
    candidate = EntityCandidate(
        id=uuid4(),
        entity_type="PHONE",
        raw_text="+91 99887 76656",
        normalized_value="+919988776656"
    )
    
    # Must not merge different phones
    status, can_id, score, evidence = resolve_candidate(db, candidate, ResolutionContext())
    assert status == "AUTO_MATCHED"
    assert can_id != existing.id
    assert len(db.added) == 1
