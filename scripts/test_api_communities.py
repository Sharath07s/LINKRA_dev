import sys
from fastapi.testclient import TestClient
from app.main import app

def test_communities_api():
    client = TestClient(app)
    
    from app.api.deps import get_current_active_user, get_db
    from app.models.user import User, Role
    
    def override_get_current_active_user():
        r = Role(name="ADMIN")
        return User(id="123", email="test@example.com", role=r, is_active=True, role_id="role123")
        
    class MockQuery:
        def filter(self, *args, **kwargs): return self
        def first(self): return Role(name="ADMIN")
    class MockDB:
        def query(self, *args, **kwargs): return MockQuery()
        
    def override_get_db():
        yield MockDB()

    app.dependency_overrides[get_current_active_user] = override_get_current_active_user
    app.dependency_overrides[get_db] = override_get_db

    print("Testing default (louvain)...")
    res1 = client.get("/api/v1/graph/analytics/communities")
    if res1.status_code != 200:
        print(f"Error {res1.status_code}: {res1.text}")
    assert res1.status_code == 200
    data1 = res1.json()
    assert data1["algorithm"] == "louvain"
    assert data1["status"] == "success"
    print("Default Louvain PASS")

    print("Testing explicit louvain...")
    res2 = client.get("/api/v1/graph/analytics/communities?algorithm=louvain")
    assert res2.status_code == 200
    data2 = res2.json()
    assert data2["algorithm"] == "louvain"
    print("Explicit Louvain PASS")

    print("Testing explicit leiden...")
    res3 = client.get("/api/v1/graph/analytics/communities?algorithm=leiden")
    assert res3.status_code == 200
    data3 = res3.json()
    assert data3["algorithm"] == "leiden"
    print("Explicit Leiden PASS")
    
    print("Testing invalid algorithm...")
    res4 = client.get("/api/v1/graph/analytics/communities?algorithm=networkx")
    assert res4.status_code == 400
    data4 = res4.json()
    assert "Invalid algorithm" in data4["detail"]
    print("Invalid algorithm rejection PASS")
    
    print("All API tests PASS.")

if __name__ == "__main__":
    test_communities_api()
