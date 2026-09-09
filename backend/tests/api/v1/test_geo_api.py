import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.api import deps
from pydantic import BaseModel

class MockUser(BaseModel):
    id: str = "mock-user-id"
    role_id: str = "role-id"
    is_active: bool = True

def override_get_current_active_user():
    return MockUser()

@pytest.fixture
def client():
    app.dependency_overrides[deps.get_current_active_user] = override_get_current_active_user
    yield TestClient(app)
    app.dependency_overrides.clear()

def test_get_crimes_geojson(client: TestClient):
    response = client.get("/api/v1/geo/crimes")
    assert response.status_code == 200
    data = response.json()
    assert data["type"] == "FeatureCollection"
    assert "features" in data
    
    if len(data["features"]) > 0:
        feature = data["features"][0]
        assert feature["type"] == "Feature"
        assert feature["geometry"]["type"] == "Point"
        assert len(feature["geometry"]["coordinates"]) == 2
        # Check standard bounds
        lon, lat = feature["geometry"]["coordinates"]
        assert -180 <= lon <= 180
        assert -90 <= lat <= 90
        
def test_get_crimes_bbox_filter(client: TestClient):
    # A bbox that includes Karnataka (roughly)
    bbox = "74.0,11.0,79.0,19.0"
    response = client.get(f"/api/v1/geo/crimes?bbox={bbox}")
    assert response.status_code == 200
    data = response.json()
    assert data["type"] == "FeatureCollection"
    
def test_get_crimes_invalid_bbox(client: TestClient):
    # Missing one coordinate
    bbox = "74.0,11.0,79.0"
    response = client.get(f"/api/v1/geo/crimes?bbox={bbox}")
    assert response.status_code == 400

def test_get_stations_geojson(client: TestClient):
    response = client.get("/api/v1/geo/stations")
    assert response.status_code == 200
    data = response.json()
    assert data["type"] == "FeatureCollection"
    assert "features" in data

def test_get_crime_density(client: TestClient):
    response = client.get("/api/v1/geo/crime-density")
    assert response.status_code == 200
    data = response.json()
    assert data["type"] == "FeatureCollection"
    assert "features" in data
    
    if len(data["features"]) > 0:
        feature = data["features"][0]
        assert feature["type"] == "Feature"
        assert feature["geometry"]["type"] == "Polygon"
        assert "cluster_id" in feature["properties"]
        assert "crime_count" in feature["properties"]
        assert feature["properties"]["crime_count"] >= 5 # minpoints is 5

def test_get_crime_density_bbox(client: TestClient):
    # A bbox that includes Karnataka (roughly)
    bbox = "74.0,11.0,79.0,19.0"
    response = client.get(f"/api/v1/geo/crime-density?bbox={bbox}")
    assert response.status_code == 200
    data = response.json()
    assert data["type"] == "FeatureCollection"

def test_get_filter_options(client: TestClient):
    response = client.get("/api/v1/geo/filter-options")
    assert response.status_code == 200
    data = response.json()
    assert "districts" in data
    assert "crime_types" in data
    assert "investigations" in data
    assert isinstance(data["districts"], list)

def test_get_crimes_with_filters(client: TestClient):
    import uuid
    dummy_uuid = str(uuid.uuid4())
    # Test that the endpoint accepts the parameters without 500 error
    response = client.get(f"/api/v1/geo/crimes?district_id={dummy_uuid}&crime_type_id={dummy_uuid}&investigation_id={dummy_uuid}&start_date=2020-01-01T00:00:00Z&end_date=2024-01-01T00:00:00Z")
    assert response.status_code == 200
    data = response.json()
    assert data["type"] == "FeatureCollection"

def test_get_crime_density_with_filters(client: TestClient):
    import uuid
    dummy_uuid = str(uuid.uuid4())
    response = client.get(f"/api/v1/geo/crime-density?district_id={dummy_uuid}&crime_type_id={dummy_uuid}&investigation_id={dummy_uuid}&start_date=2020-01-01T00:00:00Z&end_date=2024-01-01T00:00:00Z")
    assert response.status_code == 200
    data = response.json()
    assert data["type"] == "FeatureCollection"
