"""
M1.14 — Report API Tests

Tests:
 1.  Unauthorized → 401
 2.  Missing investigation → 404
 3.  Invalid UUID → 400 or 422
 4.  Empty investigation (no entities) → valid empty report
 5.  Empty report has correct structure
 6.  No fake data injected
 7.  Entity aggregation (mocked service)
 8.  Relationships included
 9.  Evidence included
10.  Anomalies correctly represented
11.  Potential links included + disclaimer present
12.  AI generation with insufficient context → safe response
13.  AI generation with mocked provider → grounded response
14.  Provider failure → deterministic fallback (not 500)
15.  M1.13/Copilot RBAC unchanged (existing router not broken)
"""
import pytest
import uuid
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from app.main import app
from app.api import deps

client = TestClient(app)

FAKE_INV_ID = str(uuid.uuid4())
MISSING_INV_ID = str(uuid.uuid4())


@pytest.fixture(autouse=True)
def override_auth():
    app.dependency_overrides[deps.get_current_active_user] = lambda: {"id": "test-user", "is_active": True}
    yield
    app.dependency_overrides.clear()


# ─────────────────────────────────────────────────────────────────────────────
# 1. RBAC — unauthenticated
# ─────────────────────────────────────────────────────────────────────────────

def test_report_unauthorized():
    app.dependency_overrides.clear()
    response = client.get(f"/api/v1/investigations/{FAKE_INV_ID}/report")
    assert response.status_code == 401


# ─────────────────────────────────────────────────────────────────────────────
# 2. Missing investigation → 404
# ─────────────────────────────────────────────────────────────────────────────

def test_report_missing_investigation():
    with patch("app.api.v1.reports.ReportingService.assemble") as mock_assemble:
        mock_assemble.side_effect = ValueError(f"Investigation {MISSING_INV_ID} not found")
        response = client.get(f"/api/v1/investigations/{MISSING_INV_ID}/report")
    assert response.status_code == 404


# ─────────────────────────────────────────────────────────────────────────────
# 3. Invalid UUID (not a valid UUID format)
# ─────────────────────────────────────────────────────────────────────────────

def test_report_invalid_uuid():
    with patch("app.api.v1.reports.ReportingService.assemble") as mock_assemble:
        mock_assemble.side_effect = ValueError("Invalid investigation UUID: not-a-uuid")
        response = client.get("/api/v1/investigations/not-a-uuid/report")
    assert response.status_code == 400


# ─────────────────────────────────────────────────────────────────────────────
# 4 & 5. Empty investigation → valid report with empty sections
# ─────────────────────────────────────────────────────────────────────────────

def _make_empty_report():
    from app.schemas.report import (
        ReportResponse, ReportInvestigationSummary,
        ReportGraphSummary, ReportGenerationMetadata
    )
    return ReportResponse(
        investigation=ReportInvestigationSummary(
            investigation_id=FAKE_INV_ID,
            status="ACTIVE",
        ),
        entities=[],
        relationships=[],
        evidence=[],
        graph_summary=ReportGraphSummary(total_entities_in_investigation=0),
        anomalies=[],
        potential_links=[],
        ai_section=None,
        metadata=ReportGenerationMetadata(
            generated_at="2026-01-01T00:00:00+00:00",
            investigation_id=FAKE_INV_ID,
            entity_count=0,
            relationship_count=0,
            evidence_count=0,
            anomaly_count=0,
            potential_link_count=0,
        ),
        limitations=["No entities are associated with this investigation."],
    )


def test_report_empty_investigation_is_valid():
    with patch("app.api.v1.reports.ReportingService.assemble", return_value=_make_empty_report()):
        response = client.get(f"/api/v1/investigations/{FAKE_INV_ID}/report")
    assert response.status_code == 200
    data = response.json()
    assert data["entities"] == []
    assert data["relationships"] == []
    assert data["evidence"] == []
    assert data["anomalies"] == []
    assert data["potential_links"] == []
    assert data["ai_section"] is None
    assert data["metadata"]["entity_count"] == 0
    assert len(data["limitations"]) > 0


def test_report_empty_investigation_no_fake_data():
    with patch("app.api.v1.reports.ReportingService.assemble", return_value=_make_empty_report()):
        response = client.get(f"/api/v1/investigations/{FAKE_INV_ID}/report")
    data = response.json()
    # Assert nothing invented
    assert data["entities"] == []
    assert data["anomalies"] == []
    assert data["potential_links"] == []


# ─────────────────────────────────────────────────────────────────────────────
# 7. Entity aggregation
# ─────────────────────────────────────────────────────────────────────────────

def test_report_entities_included():
    from app.schemas.report import ReportEntity
    report = _make_empty_report()
    report.entities = [
        ReportEntity(entity_id=str(uuid.uuid4()), name="Test Person", entity_type="PERSON")
    ]
    report.metadata.entity_count = 1

    with patch("app.api.v1.reports.ReportingService.assemble", return_value=report):
        response = client.get(f"/api/v1/investigations/{FAKE_INV_ID}/report")
    assert response.status_code == 200
    data = response.json()
    assert len(data["entities"]) == 1
    assert data["entities"][0]["name"] == "Test Person"
    assert data["entities"][0]["source_type"] == "observed"


# ─────────────────────────────────────────────────────────────────────────────
# 8. Relationships included
# ─────────────────────────────────────────────────────────────────────────────

def test_report_relationships_included():
    from app.schemas.report import ReportRelationship
    report = _make_empty_report()
    eid1, eid2 = str(uuid.uuid4()), str(uuid.uuid4())
    report.relationships = [
        ReportRelationship(
            source_entity_id=eid1, source_entity_name="Alice",
            target_entity_id=eid2, target_entity_name="Bob",
            relationship_type="COMMUNICATED_WITH",
            confidence=0.9, extraction_method="STRUCTURED_CDR"
        )
    ]
    report.metadata.relationship_count = 1

    with patch("app.api.v1.reports.ReportingService.assemble", return_value=report):
        response = client.get(f"/api/v1/investigations/{FAKE_INV_ID}/report")
    data = response.json()
    assert len(data["relationships"]) == 1
    assert data["relationships"][0]["relationship_type"] == "COMMUNICATED_WITH"
    assert data["relationships"][0]["source_type"] == "observed"


# ─────────────────────────────────────────────────────────────────────────────
# 9. Evidence included
# ─────────────────────────────────────────────────────────────────────────────

def test_report_evidence_included():
    from app.schemas.report import ReportEvidence, ReportProvenance
    report = _make_empty_report()
    report.evidence = [
        ReportEvidence(
            evidence_type="ENTITY_EXTRACTION",
            title="'John Doe' → John Doe",
            description="Extracted via spacy_ner with 90% confidence.",
            provenance=ReportProvenance(file_name="fir_001.pdf", file_type="pdf", source_type="FIR")
        )
    ]
    report.metadata.evidence_count = 1

    with patch("app.api.v1.reports.ReportingService.assemble", return_value=report):
        response = client.get(f"/api/v1/investigations/{FAKE_INV_ID}/report")
    data = response.json()
    assert len(data["evidence"]) == 1
    assert data["evidence"][0]["source_type"] == "observed"
    assert data["evidence"][0]["provenance"]["file_name"] == "fir_001.pdf"


# ─────────────────────────────────────────────────────────────────────────────
# 10. Anomalies correctly represented with disclaimer
# ─────────────────────────────────────────────────────────────────────────────

def test_report_anomalies_represented():
    from app.schemas.report import ReportAnomaly
    report = _make_empty_report()
    eid = str(uuid.uuid4())
    report.anomalies = [
        ReportAnomaly(
            anomaly_id="anom-001", entity_id=eid, entity_name="Suspect X",
            anomaly_type="HIGH_DEGREE", severity="HIGH",
            score=3.2, observed_value=18.0, baseline_value=4.5,
            reason="Degree 18 exceeds 3σ baseline of 4.5"
        )
    ]
    report.metadata.anomaly_count = 1

    with patch("app.api.v1.reports.ReportingService.assemble", return_value=report):
        response = client.get(f"/api/v1/investigations/{FAKE_INV_ID}/report")
    data = response.json()
    assert len(data["anomalies"]) == 1
    anom = data["anomalies"][0]
    assert anom["source_type"] == "structural_analysis"
    assert "disclaimer" in anom
    assert "criminal activity" in anom["disclaimer"].lower()


# ─────────────────────────────────────────────────────────────────────────────
# 11. Potential links with prediction disclaimer
# ─────────────────────────────────────────────────────────────────────────────

def test_report_potential_links_have_disclaimer():
    from app.schemas.report import ReportPotentialLink
    report = _make_empty_report()
    eid1, eid2 = str(uuid.uuid4()), str(uuid.uuid4())
    report.potential_links = [
        ReportPotentialLink(
            source_entity_id=eid1, source_entity_name="Entity A",
            target_entity_id=eid2, target_entity_name="Entity B",
            target_entity_type="PERSON", score=0.72,
            common_neighbors=3, jaccard_similarity=0.43,
            preferential_attachment_normalized=0.55,
            reason="3 common neighbors"
        )
    ]
    report.metadata.potential_link_count = 1

    with patch("app.api.v1.reports.ReportingService.assemble", return_value=report):
        response = client.get(f"/api/v1/investigations/{FAKE_INV_ID}/report")
    data = response.json()
    pl = data["potential_links"][0]
    assert pl["source_type"] == "prediction"
    assert "disclaimer" in pl
    assert "NOT a confirmed relationship" in pl["disclaimer"]


# ─────────────────────────────────────────────────────────────────────────────
# 12. AI generation with insufficient context → safe insufficient-data response
# ─────────────────────────────────────────────────────────────────────────────

def test_ai_generate_insufficient_context():
    with patch("app.api.v1.reports.ReportingService.assemble", return_value=_make_empty_report()):
        response = client.post(f"/api/v1/investigations/{FAKE_INV_ID}/report/generate")
    assert response.status_code == 200
    data = response.json()
    assert data["ai_section"] is not None
    assert data["ai_section"]["provider"] == "insufficient_data"
    assert data["ai_section"]["grounded"] is True
    assert data["ai_section"]["source_type"] == "ai_generated"
    assert "Insufficient data" in data["ai_section"]["narrative"]


# ─────────────────────────────────────────────────────────────────────────────
# 13. AI generation with mocked LLM → grounded, labeled response
# ─────────────────────────────────────────────────────────────────────────────

def test_ai_generate_grounded_response():
    from app.schemas.report import ReportEntity
    report = _make_empty_report()
    report.entities = [ReportEntity(entity_id=str(uuid.uuid4()), name="Alice", entity_type="PERSON")]
    report.metadata.entity_count = 1

    with patch("app.api.v1.reports.ReportingService.assemble", return_value=report):
        with patch("app.api.v1.reports.FallbackManager.execute_with_fallback") as mock_llm:
            mock_llm.return_value = {
                "result": "## Investigation Overview\nAlice is a canonical entity.", 
                "provider": "groq"
            }
            response = client.post(f"/api/v1/investigations/{FAKE_INV_ID}/report/generate")

    assert response.status_code == 200
    data = response.json()
    assert data["ai_section"]["provider"] == "groq"
    assert data["ai_section"]["grounded"] is True
    assert data["metadata"]["ai_generated"] is True


# ─────────────────────────────────────────────────────────────────────────────
# 14. Provider failure → deterministic fallback, not 500
# ─────────────────────────────────────────────────────────────────────────────

def test_ai_generate_provider_failure_fallback():
    from app.schemas.report import ReportEntity
    report = _make_empty_report()
    report.entities = [ReportEntity(entity_id=str(uuid.uuid4()), name="Bob", entity_type="PERSON")]
    report.metadata.entity_count = 1

    with patch("app.api.v1.reports.ReportingService.assemble", return_value=report):
        with patch("app.api.v1.reports.FallbackManager.execute_with_fallback") as mock_llm:
            mock_llm.side_effect = RuntimeError("All providers failed")
            response = client.post(f"/api/v1/investigations/{FAKE_INV_ID}/report/generate")

    assert response.status_code == 200
    data = response.json()
    assert data["ai_section"]["provider"] == "deterministic_fallback"
    assert data["ai_section"]["grounded"] is True


# ─────────────────────────────────────────────────────────────────────────────
# 15. Existing M1.13 Copilot RBAC unaffected
# ─────────────────────────────────────────────────────────────────────────────

def test_copilot_still_requires_auth():
    app.dependency_overrides.clear()
    response = client.post("/api/v1/copilot/chat", json={"message": "test"})
    assert response.status_code == 401
