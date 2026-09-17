import pytest
import uuid
import json
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timezone

from app.models.base import Base
from app.models.ingestion import IngestionJob, EntityCandidate
from app.models.resolution import CanonicalEntity
from app.models.relationship import EntityRelationship
from app.ingestion.parsers import ParsedPage
from app.nlp.relationship.extractor import (
    extract_relationships_for_page,
    LLMRelationshipResult,
    LLMRelationship
)

# Setup in-memory DB for isolated tests
_RELATIONSHIP_TABLES = [
    IngestionJob.__table__,
    EntityCandidate.__table__,
    CanonicalEntity.__table__,
    EntityRelationship.__table__,
]
engine = create_engine("sqlite:///:memory:")
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base.metadata.create_all(bind=engine, tables=_RELATIONSHIP_TABLES)

@pytest.fixture
def db():
    db = SessionLocal()
    yield db
    db.close()
    Base.metadata.drop_all(bind=engine, tables=_RELATIONSHIP_TABLES)
    Base.metadata.create_all(bind=engine, tables=_RELATIONSHIP_TABLES)

def test_structured_relationship_extraction(db, monkeypatch):
    # Mock neo4j sync to do nothing
    monkeypatch.setattr("app.nlp.relationship.extractor._sync_to_neo4j", lambda x: None)
    
    # 1. Setup mock Job and Canonical Entities
    job = IngestionJob(
        id=uuid.uuid4(),
        file_name="test_cdr.csv",
        source_type="CDR",
        file_type="csv",
    )
    db.add(job)
    
    ce1 = CanonicalEntity(id=uuid.uuid4(), entity_type="PHONE", name="1234567890")
    ce2 = CanonicalEntity(id=uuid.uuid4(), entity_type="PHONE", name="0987654321")
    db.add_all([ce1, ce2])
    db.commit()

    # 2. Setup mock ParsedPage and Candidates
    page = ParsedPage(
        page_number=1,
        text="caller: 1234567890, callee: 0987654321, timestamp: 2026-08-28T10:00:00Z",
        metadata={
            "fields": {
                "caller": "1234567890",
                "callee": "0987654321",
                "timestamp": "2026-08-28T10:00:00Z"
            }
        }
    )
    
    c1 = EntityCandidate(
        ingestion_job_id=job.id,
        entity_type="PHONE",
        raw_text="1234567890",
        extraction_method="structured_field",
        resolved_to_id=ce1.id
    )
    c2 = EntityCandidate(
        ingestion_job_id=job.id,
        entity_type="PHONE",
        raw_text="0987654321",
        extraction_method="structured_field",
        resolved_to_id=ce2.id
    )
    db.add_all([c1, c2])
    db.commit()
    
    # 3. Extract Relationships
    rels = extract_relationships_for_page(db, job, page, [c1, c2])
    
    # 4. Verify
    assert len(rels) == 1
    rel = rels[0]
    assert rel.source_entity_id == ce1.id
    assert rel.target_entity_id == ce2.id
    assert rel.relationship_type == "CONNECTED_TO"
    assert rel.confidence == 1.0
    assert rel.event_timestamp is not None
    assert rel.extraction_method == "STRUCTURED_CDR"

def test_unstructured_relationship_extraction_with_trigger(db, monkeypatch):
    job = IngestionJob(
        id=uuid.uuid4(),
        file_name="report.txt",
        source_type="FIR",
        file_type="txt",
    )
    db.add(job)
    
    ce1 = CanonicalEntity(id=uuid.uuid4(), entity_type="PERSON", name="John Doe")
    ce2 = CanonicalEntity(id=uuid.uuid4(), entity_type="PERSON", name="Jane Smith")
    db.add_all([ce1, ce2])
    db.commit()

    text = "On Monday, John Doe met with Jane Smith at the park."
    page = ParsedPage(page_number=1, text=text, metadata={})
    
    c1 = EntityCandidate(
        ingestion_job_id=job.id,
        entity_type="PERSON",
        raw_text="John Doe",
        start_offset=11,
        end_offset=19,
        extraction_method="spacy_ner",
        resolved_to_id=ce1.id
    )
    c2 = EntityCandidate(
        ingestion_job_id=job.id,
        entity_type="PERSON",
        raw_text="Jane Smith",
        start_offset=29,
        end_offset=39,
        extraction_method="spacy_ner",
        resolved_to_id=ce2.id
    )
    db.add_all([c1, c2])
    db.commit()
    
    llm_result = LLMRelationshipResult(
        relationships=[
            LLMRelationship(
                source_entity="John Doe",
                target_entity="Jane Smith",
                relationship_type="ASSOCIATED_WITH",
                confidence=0.9,
                evidence_text="John Doe met with Jane Smith at the park."
            )
        ]
    )

    with monkeypatch.context() as m:
        m.setattr("app.nlp.relationship.extractor._sync_to_neo4j", lambda x: None)
        
        class MockFB:
            @staticmethod
            def execute_with_fallback(*args, **kwargs):
                return {"result": llm_result}
                
        m.setattr("app.nlp.relationship.extractor.FallbackManager", MockFB)
        
        rels = extract_relationships_for_page(db, job, page, [c1, c2])

    assert len(rels) == 1
    rel = rels[0]
    assert rel.source_entity_id == ce1.id
    assert rel.target_entity_id == ce2.id
    assert rel.relationship_type == "ASSOCIATED_WITH"
    assert rel.confidence == 0.9
    assert rel.extraction_method == "llm_semantic"

def test_unstructured_relationship_extraction_evaluates_all_candidates(db, monkeypatch):
    monkeypatch.setattr("app.nlp.relationship.extractor._sync_to_neo4j", lambda x: None)
    
    job = IngestionJob(
        id=uuid.uuid4(),
        file_name="report.txt",
        source_type="FIR",
        file_type="txt",
    )
    db.add(job)
    
    ce1 = CanonicalEntity(id=uuid.uuid4(), entity_type="PERSON", name="John Doe")
    ce2 = CanonicalEntity(id=uuid.uuid4(), entity_type="PERSON", name="Jane Smith")
    db.add_all([ce1, ce2])
    db.commit()

    # Simple co-occurrence, no explicit trigger word
    text = "John Doe and Jane Smith were seen near the vehicle."
    page = ParsedPage(page_number=1, text=text, metadata={})
    
    c1 = EntityCandidate(
        ingestion_job_id=job.id,
        entity_type="PERSON",
        raw_text="John Doe",
        start_offset=0,
        end_offset=8,
        extraction_method="spacy_ner",
        resolved_to_id=ce1.id
    )
    c2 = EntityCandidate(
        ingestion_job_id=job.id,
        entity_type="PERSON",
        raw_text="Jane Smith",
        start_offset=13,
        end_offset=23,
        extraction_method="spacy_ner",
        resolved_to_id=ce2.id
    )
    db.add_all([c1, c2])
    db.commit()
    
    # Mock LLM to return a relationship based on this co-occurrence
    llm_result = LLMRelationshipResult(
        relationships=[
            LLMRelationship(
                source_entity="John Doe",
                target_entity="Jane Smith",
                relationship_type="ASSOCIATED_WITH",
                confidence=0.8,
                evidence_text="John Doe and Jane Smith were seen near the vehicle."
            )
        ]
    )

    class MockFB:
        @staticmethod
        def execute_with_fallback(*args, **kwargs):
            return {"result": llm_result}
            
    monkeypatch.setattr("app.nlp.relationship.extractor.FallbackManager", MockFB)
    
    rels = extract_relationships_for_page(db, job, page, [c1, c2])
    
    # The LLM should evaluate and return the relationship regardless of triggers
    assert len(rels) == 1
    assert rels[0].relationship_type == "ASSOCIATED_WITH"
