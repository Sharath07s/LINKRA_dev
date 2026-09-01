import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.config import settings
from app.api import deps
from pydantic import BaseModel

class MockUser(BaseModel):
    id: str = "mock-user-id"
    is_active: bool = True

def override_get_current_active_user():
    return MockUser()

@pytest.fixture
def chat_client():
    app.dependency_overrides[deps.get_current_active_user] = override_get_current_active_user
    yield TestClient(app)
    app.dependency_overrides.clear()

def test_chat_hello(chat_client):
    response = chat_client.post("/api/v1/chat/", json={"query": "Hello"})
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert len(data["message"]) > 0
    assert "provider" in data
    assert "timestamp" in data
    assert data["status"] == "success"

def test_chat_backend_reaches(chat_client):
    response = chat_client.post("/api/v1/chat/", json={"query": "Show theft cases in Mysuru"})
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert len(data["message"]) > 0
    assert "provider" in data
    
def test_fallback_provider(monkeypatch, chat_client):
    # Test fallback by setting an invalid primary key but a valid secondary
    # We will simulate the provider raising an exception inside the API route.
    # In a true integration test with no keys, it should hit the 500 error.
    
    # Let's test the 500 behavior when NO providers are available
    monkeypatch.setattr(settings, "OPENAI_API_KEY", None)
    monkeypatch.setattr(settings, "GEMINI_API_KEY", None)
    monkeypatch.setattr(settings, "ANTHROPIC_API_KEY", None)
    monkeypatch.setattr(settings, "DEEPSEEK_API_KEY", None)
    
    response = chat_client.post("/api/v1/chat/", json={"query": "Hello"})
    assert response.status_code == 200
    data = response.json()
    assert data["provider"] == "system_fallback"
    assert "AI providers are currently offline" in data["message"]
