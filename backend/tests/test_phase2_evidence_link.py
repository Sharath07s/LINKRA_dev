"""
backend/tests/test_phase2_evidence_link.py
==========================================
Phase 2 Evidence & Provenance test suite:
1. Relationship -> EvidenceLink creation
2. Ingestion job isolation
3. Page isolation
4. Overlapping chunks linking
5. Missing match handling
6. Character offsets verification
7. API GET /api/v1/relationship/{relationship_id}/evidence
8. Neo4j sync includes evidence_text
"""
import uuid
import pytest
from unittest.mock import patch, MagicMock

from app.db.session import SessionLocal
from app.models.ingestion import IngestionJob, EntityCandidate
from app.models.resolution import CanonicalEntity
from app.models.relationship import EntityRelationship
from app.models.document import DocumentChunk
from app.models.evidence_link import EvidenceLink
from app.ingestion.evidence_linker import (
    find_offsets_in_chunk,
    is_partial_spanning_match,
    link_evidence_for_job,
)
from app.nlp.relationship.extractor import _sync_to_neo4j


@pytest.fixture
def db():
    session = SessionLocal()
    yield session
    session.close()


def test_character_offsets_exact_and_flexible():
    chunk_content = "On the evening of 2026-08-14, suspect Suresh Rao was observed driving vehicle KA 01 AB 1234."
    ev_exact = "Suresh Rao was observed driving"
    start, end = find_offsets_in_chunk(ev_exact, chunk_content)
    assert start is not None and end is not None
    assert chunk_content[start:end] == ev_exact

    # Flexible whitespace with newline
    ev_with_ws = "Suresh Rao\nwas observed   driving"
    start_ws, end_ws = find_offsets_in_chunk(ev_with_ws, chunk_content)
    assert start_ws is not None and end_ws is not None
    assert start_ws == start


def test_spanning_match_detection():
    # Chunk contains only prefix of long evidence
    chunk_0 = "The suspect was seen leaving the scene while she was returning home from her workplace at Infosys."
    chunk_1 = "workplace at Infosys Technologies Limited after her shift ended late."
    full_ev = "she was returning home from her workplace at Infosys Technologies Limited"

    spanning_0, start_0, end_0 = is_partial_spanning_match(full_ev, chunk_0)
    assert spanning_0 is True
    assert start_0 is not None

    spanning_1, start_1, end_1 = is_partial_spanning_match(full_ev, chunk_1)
    assert spanning_1 is True
    assert start_1 is not None


def test_evidence_link_creation_and_offsets(db):
    test_id = uuid.uuid4()
    job = IngestionJob(
        id=test_id,
        file_name="test_report_p2.txt",
        source_type="FIR",
        file_type="txt",
        status="PROCESSING"
    )
    db.add(job)

    # Add canonical entities
    e1 = CanonicalEntity(id=uuid.uuid4(), entity_type="PERSON", name="Priya Sharma")
    e2 = CanonicalEntity(id=uuid.uuid4(), entity_type="ORGANIZATION", name="Infosys")
    db.add_all([e1, e2])
    db.flush()

    # Add EntityRelationship
    ev_text = "she was returning home from her workplace at Infosys Technologies Limited"
    rel = EntityRelationship(
        id=uuid.uuid4(),
        source_entity_id=e1.id,
        target_entity_id=e2.id,
        relationship_type="WORKS_FOR",
        confidence=0.95,
        extraction_method="llm_semantic",
        evidence_text=ev_text,
        ingestion_job_id=job.id,
        source_page=1,
    )
    db.add(rel)

    # Add DocumentChunk on Page 1
    content = f"First Information Report. Complainant states that {ev_text} on Monday evening."
    chunk = DocumentChunk(
        id=uuid.uuid4(),
        source_id="test_report_p2.txt",
        content=content,
        metadata_json={
            "ingestion_job_id": str(job.id),
            "page_number": 1,
            "chunk_index": 0,
            "source_filename": "test_report_p2.txt"
        }
    )
    db.add(chunk)
    db.commit()

    try:
        # Test 1 & 6: Execute linker
        links = link_evidence_for_job(db, job)
        assert len(links) == 1
        link = links[0]

        assert link.relationship_id == rel.id
        assert link.document_chunk_id == chunk.id
        assert link.quote_snippet == ev_text
        assert link.char_start is not None
        assert link.char_end is not None
        assert chunk.content[link.char_start:link.char_end] == ev_text
    finally:
        # Clean up
        db.query(EvidenceLink).filter(EvidenceLink.relationship_id == rel.id).delete()
        db.query(EntityRelationship).filter(EntityRelationship.id == rel.id).delete()
        db.query(DocumentChunk).filter(DocumentChunk.id == chunk.id).delete()
        db.query(CanonicalEntity).filter(CanonicalEntity.id.in_([e1.id, e2.id])).delete()
        db.query(IngestionJob).filter(IngestionJob.id == job.id).delete()
        db.commit()


def test_ingestion_job_isolation(db):
    job_a = IngestionJob(id=uuid.uuid4(), file_name="doc_a.txt", source_type="FIR", file_type="txt")
    job_b = IngestionJob(id=uuid.uuid4(), file_name="doc_b.txt", source_type="FIR", file_type="txt")
    db.add_all([job_a, job_b])

    e1 = CanonicalEntity(id=uuid.uuid4(), entity_type="PERSON", name="Shared Subject")
    e2 = CanonicalEntity(id=uuid.uuid4(), entity_type="ORGANIZATION", name="Shared Org")
    db.add_all([e1, e2])
    db.flush()

    identical_evidence = "Subject met at the cafe at 4 PM"

    rel_a = EntityRelationship(
        id=uuid.uuid4(),
        source_entity_id=e1.id,
        target_entity_id=e2.id,
        relationship_type="MET_AT",
        confidence=0.9,
        extraction_method="llm_semantic",
        evidence_text=identical_evidence,
        ingestion_job_id=job_a.id,
        source_page=1,
    )
    db.add(rel_a)

    # Chunk belonging strictly to Job B
    chunk_b = DocumentChunk(
        id=uuid.uuid4(),
        source_id="doc_b.txt",
        content=f"Incident B: {identical_evidence} outside city.",
        metadata_json={"ingestion_job_id": str(job_b.id), "page_number": 1, "chunk_index": 0}
    )
    db.add(chunk_b)
    db.commit()

    try:
        # Link for Job A — must NOT link to Job B's chunk even though text matches
        links_a = link_evidence_for_job(db, job_a)
        assert len(links_a) == 0, "Job A relationship linked to Job B chunk (Isolation violation!)"
    finally:
        db.query(EvidenceLink).filter(EvidenceLink.relationship_id == rel_a.id).delete()
        db.query(EntityRelationship).filter(EntityRelationship.id == rel_a.id).delete()
        db.query(DocumentChunk).filter(DocumentChunk.id == chunk_b.id).delete()
        db.query(CanonicalEntity).filter(CanonicalEntity.id.in_([e1.id, e2.id])).delete()
        db.query(IngestionJob).filter(IngestionJob.id.in_([job_a.id, job_b.id])).delete()
        db.commit()


def test_page_isolation(db):
    job = IngestionJob(id=uuid.uuid4(), file_name="multipage.txt", source_type="FIR", file_type="txt")
    db.add(job)
    e1 = CanonicalEntity(id=uuid.uuid4(), entity_type="PERSON", name="Suspect")
    e2 = CanonicalEntity(id=uuid.uuid4(), entity_type="LOCATION", name="Station")
    db.add_all([e1, e2])
    db.flush()

    ev_text = "Suspect was brought to the Central Police Station."
    # Relationship on Page 2
    rel = EntityRelationship(
        id=uuid.uuid4(),
        source_entity_id=e1.id,
        target_entity_id=e2.id,
        relationship_type="LOCATED_AT",
        confidence=0.9,
        extraction_method="llm_semantic",
        evidence_text=ev_text,
        ingestion_job_id=job.id,
        source_page=2,
    )
    db.add(rel)

    # Chunk with identical text on Page 1
    chunk_p1 = DocumentChunk(
        id=uuid.uuid4(),
        source_id="multipage.txt",
        content=f"Preliminary Notes: {ev_text}",
        metadata_json={"ingestion_job_id": str(job.id), "page_number": 1, "chunk_index": 0}
    )
    # Chunk with identical text on Page 2
    chunk_p2 = DocumentChunk(
        id=uuid.uuid4(),
        source_id="multipage.txt",
        content=f"Official Statement: {ev_text}",
        metadata_json={"ingestion_job_id": str(job.id), "page_number": 2, "chunk_index": 0}
    )
    db.add_all([chunk_p1, chunk_p2])
    db.commit()

    try:
        links = link_evidence_for_job(db, job)
        assert len(links) == 1
        assert links[0].document_chunk_id == chunk_p2.id, "Linked to chunk on Page 1 instead of Page 2"
    finally:
        db.query(EvidenceLink).filter(EvidenceLink.relationship_id == rel.id).delete()
        db.query(EntityRelationship).filter(EntityRelationship.id == rel.id).delete()
        db.query(DocumentChunk).filter(DocumentChunk.id.in_([chunk_p1.id, chunk_p2.id])).delete()
        db.query(CanonicalEntity).filter(CanonicalEntity.id.in_([e1.id, e2.id])).delete()
        db.query(IngestionJob).filter(IngestionJob.id == job.id).delete()
        db.commit()


def test_overlapping_chunks_link_to_both(db):
    job = IngestionJob(id=uuid.uuid4(), file_name="overlap_test.txt", source_type="FIR", file_type="txt")
    db.add(job)
    e1 = CanonicalEntity(id=uuid.uuid4(), entity_type="PERSON", name="Ravi")
    e2 = CanonicalEntity(id=uuid.uuid4(), entity_type="VEHICLE", name="Motorcycle")
    db.add_all([e1, e2])
    db.flush()

    ev_text = "Ravi Kumar operated the motorcycle bearing plate KA 01 AB 1234"
    rel = EntityRelationship(
        id=uuid.uuid4(),
        source_entity_id=e1.id,
        target_entity_id=e2.id,
        relationship_type="USES",
        confidence=0.95,
        extraction_method="llm_semantic",
        evidence_text=ev_text,
        ingestion_job_id=job.id,
        source_page=1,
    )
    db.add(rel)

    # Overlapping chunks both containing the evidence
    chunk_0 = DocumentChunk(
        id=uuid.uuid4(),
        source_id="overlap_test.txt",
        content=f"...beginning of page... {ev_text} ...end of chunk 0...",
        metadata_json={"ingestion_job_id": str(job.id), "page_number": 1, "chunk_index": 0}
    )
    chunk_1 = DocumentChunk(
        id=uuid.uuid4(),
        source_id="overlap_test.txt",
        content=f"...overlap start... {ev_text} ...rest of chunk 1...",
        metadata_json={"ingestion_job_id": str(job.id), "page_number": 1, "chunk_index": 1}
    )
    db.add_all([chunk_0, chunk_1])
    db.commit()

    try:
        links = link_evidence_for_job(db, job)
        assert len(links) == 2, "Failed to link to both overlapping chunks"
        linked_chunk_ids = {l.document_chunk_id for l in links}
        assert chunk_0.id in linked_chunk_ids
        assert chunk_1.id in linked_chunk_ids
    finally:
        db.query(EvidenceLink).filter(EvidenceLink.relationship_id == rel.id).delete()
        db.query(EntityRelationship).filter(EntityRelationship.id == rel.id).delete()
        db.query(DocumentChunk).filter(DocumentChunk.id.in_([chunk_0.id, chunk_1.id])).delete()
        db.query(CanonicalEntity).filter(CanonicalEntity.id.in_([e1.id, e2.id])).delete()
        db.query(IngestionJob).filter(IngestionJob.id == job.id).delete()
        db.commit()


def test_missing_match_handling(db):
    job = IngestionJob(id=uuid.uuid4(), file_name="nomatch.txt", source_type="FIR", file_type="txt")
    db.add(job)
    e1 = CanonicalEntity(id=uuid.uuid4(), entity_type="PERSON", name="Alpha")
    e2 = CanonicalEntity(id=uuid.uuid4(), entity_type="PERSON", name="Beta")
    db.add_all([e1, e2])
    db.flush()

    rel = EntityRelationship(
        id=uuid.uuid4(),
        source_entity_id=e1.id,
        target_entity_id=e2.id,
        relationship_type="ASSOCIATED_WITH",
        confidence=0.8,
        extraction_method="llm_semantic",
        evidence_text="Completely unmatched sentence that never appears in document.",
        ingestion_job_id=job.id,
        source_page=1,
    )
    db.add(rel)

    chunk = DocumentChunk(
        id=uuid.uuid4(),
        source_id="nomatch.txt",
        content="Different text entirely about weather and sports.",
        metadata_json={"ingestion_job_id": str(job.id), "page_number": 1, "chunk_index": 0}
    )
    db.add(chunk)
    db.commit()

    try:
        links = link_evidence_for_job(db, job)
        assert len(links) == 0, "Fabricated evidence link when no text matched"
        # Verify relationship remains intact
        surviving_rel = db.get(EntityRelationship, rel.id)
        assert surviving_rel is not None
        assert surviving_rel.evidence_text == rel.evidence_text
    finally:
        db.query(EvidenceLink).filter(EvidenceLink.relationship_id == rel.id).delete()
        db.query(EntityRelationship).filter(EntityRelationship.id == rel.id).delete()
        db.query(DocumentChunk).filter(DocumentChunk.id == chunk.id).delete()
        db.query(CanonicalEntity).filter(CanonicalEntity.id.in_([e1.id, e2.id])).delete()
        db.query(IngestionJob).filter(IngestionJob.id == job.id).delete()
        db.commit()


def test_neo4j_sync_passes_evidence_text():
    mock_session = MagicMock()
    mock_neo4j = MagicMock()
    mock_neo4j.get_session.return_value.__enter__.return_value = mock_session

    rel = EntityRelationship(
        id=uuid.uuid4(),
        source_entity_id=uuid.uuid4(),
        target_entity_id=uuid.uuid4(),
        relationship_type="OWNS",
        confidence=0.98,
        extraction_method="llm_semantic",
        evidence_text="Jane Doe holds title to the vehicle.",
        ingestion_job_id=uuid.uuid4(),
        source_page=3,
        source_row=None,
    )

    with patch("app.nlp.relationship.extractor.neo4j_intelligence", mock_neo4j):
        _sync_to_neo4j([rel])

    mock_session.run.assert_called_once()
    call_args = mock_session.run.call_args
    query_str = call_args[0][0]
    params = call_args[0][1]

    assert "r.evidence_text = $evidence_text" in query_str
    assert params["evidence_text"] == "Jane Doe holds title to the vehicle."
    assert params["source_page"] == 3
    assert params["confidence"] == 0.98


def test_get_relationship_evidence_api(db):
    from fastapi.testclient import TestClient
    from app.main import app
    from app.api import deps
    from app.models.user import User

    job = IngestionJob(id=uuid.uuid4(), file_name="api_evidence_test.txt", source_type="FIR", file_type="txt")
    db.add(job)
    e1 = CanonicalEntity(id=uuid.uuid4(), entity_type="PERSON", name="API Complainant")
    e2 = CanonicalEntity(id=uuid.uuid4(), entity_type="ORGANIZATION", name="API Org")
    db.add_all([e1, e2])
    db.flush()

    ev_text = "The complainant was returning home from API Org offices."
    rel = EntityRelationship(
        id=uuid.uuid4(),
        source_entity_id=e1.id,
        target_entity_id=e2.id,
        relationship_type="WORKS_FOR",
        confidence=0.92,
        extraction_method="llm_semantic",
        evidence_text=ev_text,
        ingestion_job_id=job.id,
        source_page=1,
    )
    db.add(rel)

    chunk = DocumentChunk(
        id=uuid.uuid4(),
        source_id="api_evidence_test.txt",
        content=f"Report excerpt: {ev_text}",
        metadata_json={
            "ingestion_job_id": str(job.id),
            "page_number": 1,
            "chunk_index": 0,
            "source_filename": "api_evidence_test.txt"
        }
    )
    db.add(chunk)

    link = EvidenceLink(
        id=uuid.uuid4(),
        relationship_id=rel.id,
        document_chunk_id=chunk.id,
        char_start=16,
        char_end=16 + len(ev_text),
        quote_snippet=ev_text,
        confidence=1.0,
    )
    db.add(link)
    db.commit()

    # Mock authenticated user with ANALYST role
    from app.models.user import Role
    from app.api.v1.relationship import allow_analysts
    mock_role = Role(id=uuid.uuid4(), name="ANALYST")
    mock_user = User(
        id=uuid.uuid4(),
        email="analyst@kcia.gov.in",
        first_name="Analyst",
        last_name="User",
        is_active=True,
        role_id=mock_role.id,
        role=mock_role,
    )
    db.add_all([mock_role, mock_user])
    db.commit()

    app.dependency_overrides[deps.get_current_active_user] = lambda: mock_user
    app.dependency_overrides[allow_analysts] = lambda: mock_user
    app.dependency_overrides[deps.get_db] = lambda: db
    client = TestClient(app)

    try:
        resp = client.get(f"/api/v1/relationship/{rel.id}/evidence")
        assert resp.status_code == 200, f"API failed with {resp.status_code}: {resp.text}"
        data = resp.json()

        assert data["relationship_id"] == str(rel.id)
        assert data["relationship_type"] == "WORKS_FOR"
        assert data["confidence"] == 0.92
        assert data["evidence_text"] == ev_text
        assert data["source_filename"] == "api_evidence_test.txt"
        assert data["source_page"] == 1
        assert len(data["evidence_links"]) == 1

        ev_link = data["evidence_links"][0]
        assert ev_link["evidence_link_id"] == str(link.id)
        assert ev_link["document_chunk_id"] == str(chunk.id)
        assert ev_link["quote_snippet"] == ev_text
        assert ev_link["char_start"] == 16
        assert ev_link["chunk_index"] == 0
        assert ev_link["source_filename"] == "api_evidence_test.txt"
    finally:
        app.dependency_overrides.clear()
        db.query(EvidenceLink).filter(EvidenceLink.relationship_id == rel.id).delete()
        db.query(EntityRelationship).filter(EntityRelationship.id == rel.id).delete()
        db.query(DocumentChunk).filter(DocumentChunk.id == chunk.id).delete()
        db.query(CanonicalEntity).filter(CanonicalEntity.id.in_([e1.id, e2.id])).delete()
        db.query(IngestionJob).filter(IngestionJob.id == job.id).delete()
        db.query(User).filter(User.id == mock_user.id).delete()
        db.query(Role).filter(Role.id == mock_role.id).delete()
        db.commit()

