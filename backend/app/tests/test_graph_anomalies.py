import pytest
from fastapi.testclient import TestClient

def test_get_top_anomalies(admin_client: TestClient):
    # Test top anomalies reachability and schema
    response = admin_client.get("/api/v1/graph/anomalies/top?limit=10")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "anomalies" in data
    assert isinstance(data["anomalies"], list)

def test_get_anomalies_for_entity(admin_client: TestClient):
    # Test specific entity anomalies reachability
    # For a non-existent entity, it might return 404 or insufficient_data
    response = admin_client.get("/api/v1/graph/anomalies/fake-entity-id")
    # depending on graph size it could be 200 (insufficient_data) or 404 (not found)
    assert response.status_code in [200, 404]
    
    if response.status_code == 200:
        data = response.json()
        assert "status" in data
        assert data["status"] == "insufficient_data"
        assert "anomalies" in data
        assert isinstance(data["anomalies"], list)

def test_unauthenticated_access(client: TestClient):
    response = client.get("/api/v1/graph/anomalies/top")
    assert response.status_code == 401
