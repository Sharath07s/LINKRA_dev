import pytest
from uuid import uuid4
from sqlalchemy.orm import Session
from app.models.investigation import Investigation, InvestigationEntity
from app.models.crime import Crime
from app.models.resolution import CanonicalEntity
from datetime import datetime

def test_add_and_get_investigation_entities(auth_client, db: Session):
    # 1. Setup mock data
    inv_id = uuid4()
    entity_id = uuid4()
    crime_id = uuid4()
    
    crime = Crime(id=crime_id, title="Test Crime", occurrence_date=datetime.now())
    db.add(crime)
    db.flush()
    
    inv = Investigation(id=inv_id, status="ACTIVE", crime_id=crime_id)
    db.add(inv)
    
    canonical = CanonicalEntity(id=entity_id, entity_type="PERSON", name="Test Subject")
    db.add(canonical)
    
    db.commit()
    
    # 2. Add entity to investigation
    payload = {
        "investigation_id": str(inv_id),
        "entity_id": str(entity_id)
    }
    
    r = auth_client.post(
        f"/api/v1/investigations/{inv_id}/entities",
        json=payload
    )
    assert r.status_code == 200
    data = r.json()
    assert data["entity_id"] == str(entity_id)
    assert data["investigation_id"] == str(inv_id)
    
    # 3. Get entities
    r2 = auth_client.get(
        f"/api/v1/investigations/{inv_id}/entities"
    )
    assert r2.status_code == 200
    data2 = r2.json()
    assert len(data2) == 1
    assert data2[0]["entity_id"] == str(entity_id)
    assert data2[0]["entity"]["name"] == "Test Subject"
    
    # 4. Try adding non-existent entity
    fake_entity = uuid4()
    r3 = auth_client.post(
        f"/api/v1/investigations/{inv_id}/entities",
        json={"investigation_id": str(inv_id), "entity_id": str(fake_entity)}
    )
    assert r3.status_code == 404
    
    # 5. Delete entity
    r4 = auth_client.delete(
        f"/api/v1/investigations/{inv_id}/entities/{entity_id}"
    )
    assert r4.status_code == 200
    
    # Verify deletion
    r5 = auth_client.get(
        f"/api/v1/investigations/{inv_id}/entities"
    )
    assert r5.status_code == 200
    assert len(r5.json()) == 0
