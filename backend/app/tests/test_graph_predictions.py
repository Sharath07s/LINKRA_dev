import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.api import deps

client = TestClient(app)

@pytest.fixture
def auth_headers():
    return {"Authorization": "Bearer test-token"}

@pytest.fixture(autouse=True)
def override_auth():
    app.dependency_overrides[deps.get_current_active_user] = lambda: {"id": "test-user", "is_active": True}
    yield
    app.dependency_overrides.clear()

def test_get_potential_links_unauthorized():
    # Remove the dependency override temporarily for this test
    app.dependency_overrides.clear()
    response = client.get("/api/v1/graph/potential-links/some-uuid")
    assert response.status_code == 401

def test_get_potential_links_invalid_uuid(auth_headers, monkeypatch):
    response = client.get("/api/v1/graph/potential-links/invalid-uuid", headers=auth_headers)
    # The neo4j layer should return 404 since "invalid-uuid" won't match any node in Neo4j
    # Assuming it's safely returning the not_found status.
    assert response.status_code in [404, 422]

def test_get_potential_links_empty_graph(auth_headers, monkeypatch):
    """
    Mock the service to return insufficient_data
    """
    from app.ai.neo4j.predictions import neo4j_predictions
    
    def mock_get_links(*args, **kwargs):
        return {
            "status": "insufficient_data",
            "potential_links": [],
            "reason": "Entity has insufficient connections."
        }
        
    monkeypatch.setattr(neo4j_predictions, "get_potential_links_for_entity", mock_get_links)
    
    response = client.get("/api/v1/graph/potential-links/123e4567-e89b-12d3-a456-426614174000", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "insufficient_data"
    assert len(data["potential_links"]) == 0

def test_get_potential_links_success(auth_headers, monkeypatch):
    from app.ai.neo4j.predictions import neo4j_predictions
    
    def mock_get_links(*args, **kwargs):
        return {
            "status": "success",
            "potential_links": [
                {
                    "source_entity_id": "a-id",
                    "target_entity_id": "b-id",
                    "target_entity_name": "Target B",
                    "target_entity_type": "Person",
                    "score": 0.85,
                    "signals": {
                        "common_neighbors": 4,
                        "jaccard_similarity": 0.5,
                        "preferential_attachment_normalized": 1.0
                    },
                    "weights": {
                        "common_neighbors": 0.40,
                        "jaccard": 0.40,
                        "preferential_attachment": 0.20
                    },
                    "explanation": {
                        "reason": "The candidate shares 4 common neighbors with the focal entity and has overlapping local topology (50%).",
                        "method": "common_neighbors + jaccard + preferential_attachment"
                    }
                }
            ],
            "reason": None
        }
        
    monkeypatch.setattr(neo4j_predictions, "get_potential_links_for_entity", mock_get_links)
    
    response = client.get("/api/v1/graph/potential-links/123e4567-e89b-12d3-a456-426614174000", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert len(data["potential_links"]) == 1
    assert data["potential_links"][0]["target_entity_id"] == "b-id"
    assert data["potential_links"][0]["score"] == 0.85
