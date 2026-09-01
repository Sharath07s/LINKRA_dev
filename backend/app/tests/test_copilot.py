import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from app.main import app
from app.api import deps

client = TestClient(app)


@pytest.fixture(autouse=True)
def override_auth():
    app.dependency_overrides[deps.get_current_active_user] = lambda: {"id": "test-user", "is_active": True}
    yield
    app.dependency_overrides.clear()


# ─────────────────────────────────────────────────────────────────────────────
# 1. RBAC — unauthenticated requests must be blocked
# ─────────────────────────────────────────────────────────────────────────────

def test_copilot_unauthorized():
    """Ensure /copilot/chat returns 401 when not authenticated."""
    app.dependency_overrides.clear()  # Remove the auth override for this test
    response = client.post("/api/v1/copilot/chat", json={"message": "What are the anomalies?"})
    assert response.status_code == 401


# ─────────────────────────────────────────────────────────────────────────────
# 2. Intent routing — rule-based classification
# ─────────────────────────────────────────────────────────────────────────────

def test_intent_router_anomaly():
    from app.ai.copilot.intent_router import IntentRouter
    from app.schemas.copilot import CopilotIntent
    intent = IntentRouter.get_intent("Why was this entity flagged as anomalous?")
    assert intent == CopilotIntent.ANOMALY_EXPLANATION


def test_intent_router_potential_link():
    from app.ai.copilot.intent_router import IntentRouter
    from app.schemas.copilot import CopilotIntent
    intent = IntentRouter.get_intent("Why is there a potential link between suspect A and suspect B?")
    assert intent == CopilotIntent.POTENTIAL_LINK_EXPLANATION


def test_intent_router_evidence():
    from app.ai.copilot.intent_router import IntentRouter
    from app.schemas.copilot import CopilotIntent
    intent = IntentRouter.get_intent("What is the evidence supporting this?")
    assert intent == CopilotIntent.EVIDENCE_LOOKUP


def test_intent_router_entity():
    from app.ai.copilot.intent_router import IntentRouter
    from app.schemas.copilot import CopilotIntent
    intent = IntentRouter.get_intent("Who is Rajan Gupta?")
    assert intent == CopilotIntent.ENTITY_LOOKUP


# ─────────────────────────────────────────────────────────────────────────────
# 3. INSUFFICIENT_DATA — graceful no-context response
# ─────────────────────────────────────────────────────────────────────────────

def test_copilot_no_entity_context_returns_insufficient(auth_headers=None):
    """When a non-general intent is sent without an entity_id, return INSUFFICIENT_DATA."""
    with patch("app.ai.copilot.orchestrator.CopilotOrchestrator.handle_query") as mock_handle:
        from app.schemas.copilot import CopilotResponse, CopilotIntent
        mock_handle.return_value = CopilotResponse(
            status="INSUFFICIENT_DATA",
            answer="I could not find verified evidence or entities matching your query.",
            intent=CopilotIntent.ANOMALY_EXPLANATION,
            grounded=True
        )
        response = client.post("/api/v1/copilot/chat", json={
            "message": "Why was this entity flagged as anomalous?",
        })
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "INSUFFICIENT_DATA"
        assert data["grounded"] is True


# ─────────────────────────────────────────────────────────────────────────────
# 4. Grounded response — provider returns answer with evidence
# ─────────────────────────────────────────────────────────────────────────────

def test_copilot_answered_response():
    """Simulate successful LLM response with evidence."""
    with patch("app.ai.copilot.orchestrator.CopilotOrchestrator.handle_query") as mock_handle:
        from app.schemas.copilot import CopilotResponse, CopilotIntent
        mock_handle.return_value = CopilotResponse(
            status="ANSWERED",
            answer="This entity has a high degree centrality score.",
            intent=CopilotIntent.ANOMALY_EXPLANATION,
            provider="groq",
            evidence=[{"type": "ENTITY_EXTRACTION", "title": "Source A", "description": "Extracted via NLP"}],
            grounded=True
        )
        response = client.post("/api/v1/copilot/chat", json={
            "message": "Why was entity X flagged as an anomaly?",
            "entity_id": "00000000-0000-0000-0000-000000000001"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ANSWERED"
        assert data["grounded"] is True
        assert len(data["evidence"]) > 0
        assert "hallucinated" not in data["answer"].lower()


# ─────────────────────────────────────────────────────────────────────────────
# 5. Provider unavailable — deterministic fallback
# ─────────────────────────────────────────────────────────────────────────────

def test_copilot_provider_unavailable_returns_deterministic():
    """When LLM is unavailable, should return deterministic fallback, not an error."""
    with patch("app.ai.copilot.orchestrator.CopilotOrchestrator.handle_query") as mock_handle:
        from app.schemas.copilot import CopilotResponse, CopilotIntent
        mock_handle.return_value = CopilotResponse(
            status="PROVIDER_UNAVAILABLE",
            answer="*AI Provider Unavailable. Showing deterministic structured context.*",
            intent=CopilotIntent.ANOMALY_EXPLANATION,
            provider="deterministic_fallback",
            grounded=True
        )
        response = client.post("/api/v1/copilot/chat", json={
            "message": "Explain the anomaly?",
            "entity_id": "00000000-0000-0000-0000-000000000001"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "PROVIDER_UNAVAILABLE"
        assert data["provider"] == "deterministic_fallback"
        assert data["grounded"] is True


# ─────────────────────────────────────────────────────────────────────────────
# 6. Schema validation — empty message must be rejected
# ─────────────────────────────────────────────────────────────────────────────

def test_copilot_empty_message_rejected():
    """Empty message should fail schema validation."""
    response = client.post("/api/v1/copilot/chat", json={"message": ""})
    assert response.status_code == 422


# ─────────────────────────────────────────────────────────────────────────────
# 7. Schema validation — oversized message must be rejected
# ─────────────────────────────────────────────────────────────────────────────

def test_copilot_oversized_message_rejected():
    """Message exceeding max_length=2000 should fail schema validation."""
    response = client.post("/api/v1/copilot/chat", json={"message": "x" * 2001})
    assert response.status_code == 422
