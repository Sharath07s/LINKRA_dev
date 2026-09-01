from fastapi.testclient import TestClient

def test_read_suspects_empty(auth_client: TestClient):
    response = auth_client.get("/api/v1/suspects/")
    assert response.status_code == 200
    assert response.json() == []

def test_create_suspect(admin_client: TestClient):
    data = {
        "full_name": "John Doe",
        "alias_name": "Johnny",
        "gender": "Male",
        "age": 30
    }
    response = admin_client.post("/api/v1/suspects/", json=data)
    assert response.status_code == 200
    content = response.json()
    assert content["full_name"] == data["full_name"]
    assert "id" in content

    # Fetch it back
    suspect_id = content["id"]
    response = admin_client.get(f"/api/v1/suspects/{suspect_id}")
    assert response.status_code == 200
    assert response.json()["id"] == suspect_id

def test_update_suspect(admin_client: TestClient):
    data = {"full_name": "Jane Doe"}
    response = admin_client.post("/api/v1/suspects/", json=data)
    suspect_id = response.json()["id"]

    update_data = {"full_name": "Jane Smith"}
    response = admin_client.put(f"/api/v1/suspects/{suspect_id}", json=update_data)
    assert response.status_code == 200
    assert response.json()["full_name"] == "Jane Smith"

def test_get_nonexistent_suspect(auth_client: TestClient):
    response = auth_client.get("/api/v1/suspects/00000000-0000-0000-0000-000000000000")
    assert response.status_code == 404
