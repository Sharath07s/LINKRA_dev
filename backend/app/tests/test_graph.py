import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.api import deps
from pydantic import BaseModel

class MockRole(BaseModel):
    id: str = "role-id"
    name: str = "OFFICER"

class MockUser(BaseModel):
    id: str = "mock-user-id"
    role_id: str = "role-id"
    is_active: bool = True

class MockQuery:
    def __init__(self, model, result=None):
        self.model = model
        self.result = result
    def filter(self, *args, **kwargs):
        return self
    def first(self):
        return self.result

class MockSession:
    def __init__(self, role_name="OFFICER"):
        self.role_name = role_name
    def query(self, model):
        from app.models.user import Role
        if model == Role:
            return MockQuery(model, MockRole(name=self.role_name))
        return MockQuery(model, None)

def override_get_current_active_user():
    return MockUser()

@pytest.fixture
def graph_client():
    app.dependency_overrides[deps.get_current_active_user] = override_get_current_active_user
    def get_mock_db():
        yield MockSession(role_name="OFFICER")
    app.dependency_overrides[deps.get_db] = get_mock_db
    yield TestClient(app)
    app.dependency_overrides.clear()

def test_get_entity_node_unauthorized():
    app.dependency_overrides.clear()
    client = TestClient(app)
    response = client.get("/api/v1/graph/entity/test-id")
    assert response.status_code == 401

def test_get_entity_neighborhood_authorized(graph_client):
    response = graph_client.get("/api/v1/graph/subgraph/test-id?depth=1&max_nodes=10")
    assert response.status_code == 200
    data = response.json()
    assert "nodes" in data
    assert "edges" in data
    assert data["center_entity_id"] == "test-id"
