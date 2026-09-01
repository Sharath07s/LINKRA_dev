import pytest
from fastapi.testclient import TestClient
from uuid import uuid4

def test_get_entity_explainability_not_found(auth_client: TestClient):
    """Test retrieving explainability for a non-existent entity."""
    random_id = str(uuid4())
    response = auth_client.get(f"/api/v1/explainability/entity/{random_id}")
    assert response.status_code == 404
    assert response.json()["detail"] == "Entity not found"

def test_get_entity_explainability_unauthorized(client: TestClient):
    """Test retrieving explainability without auth."""
    random_id = str(uuid4())
    response = client.get(f"/api/v1/explainability/entity/{random_id}")
    assert response.status_code == 401
