import pytest
from fastapi.testclient import TestClient

def test_get_entity_degree(admin_client: TestClient):
    response = admin_client.get("/api/v1/graph/analytics/degree/fake-id")
    assert response.status_code == 200
    data = response.json()
    assert "total_degree" in data
    assert "in_degree" in data
    assert "out_degree" in data
    assert data["total_degree"] >= 0

def test_get_degree_centrality(admin_client: TestClient):
    response = admin_client.get("/api/v1/graph/analytics/centrality/degree?limit=5")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

def test_get_shortest_path(admin_client: TestClient):
    response = admin_client.get("/api/v1/graph/analytics/shortest-path?source=fake1&target=fake2&max_depth=3")
    assert response.status_code == 200
    data = response.json()
    assert "path_exists" in data
    assert "length" in data
    assert "nodes" in data
    assert "edges" in data

def test_get_relationship_distribution(admin_client: TestClient):
    response = admin_client.get("/api/v1/graph/analytics/distribution/fake-id")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

def test_get_local_component(admin_client: TestClient):
    response = admin_client.get("/api/v1/graph/analytics/component/fake-id?max_depth=2")
    assert response.status_code == 200
    data = response.json()
    assert "component_size" in data
    assert data["component_size"] >= 1
