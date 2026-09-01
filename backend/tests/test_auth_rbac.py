import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.api import deps
from pydantic import BaseModel

class MockRole(BaseModel):
    id: str = "role-id"
    name: str = "ADMIN"

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
    def count(self):
        return 0
    def all(self):
        return []

class MockSession:
    def __init__(self, role_name="ADMIN"):
        self.role_name = role_name
    def query(self, model):
        from app.models.user import Role
        if model == Role:
            return MockQuery(model, MockRole(name=self.role_name))
        return MockQuery(model, None)

def override_get_current_active_user():
    return MockUser()

@pytest.fixture
def rbac_client():
    app.dependency_overrides[deps.get_current_active_user] = override_get_current_active_user
    yield TestClient(app)
    app.dependency_overrides.clear()

def set_role(role_name):
    def get_mock_db():
        yield MockSession(role_name=role_name)
    app.dependency_overrides[deps.get_db] = get_mock_db

def test_admin_access(rbac_client):
    set_role("ADMIN")
    response = rbac_client.get("/api/v1/infrastructure/metrics")
    assert response.status_code == 200

def test_officer_denied_admin_route(rbac_client):
    set_role("OFFICER")
    response = rbac_client.get("/api/v1/infrastructure/metrics")
    assert response.status_code == 403

def test_executive_access_fusion(rbac_client):
    set_role("EXECUTIVE")
    response = rbac_client.get("/api/v1/fusion/signals")
    assert response.status_code == 200

def test_officer_denied_fusion(rbac_client):
    set_role("OFFICER")
    response = rbac_client.get("/api/v1/fusion/signals")
    assert response.status_code == 403

def test_missing_auth():
    app.dependency_overrides.clear()
    client = TestClient(app)
    response = client.get("/api/v1/infrastructure/metrics")
    assert response.status_code == 401
