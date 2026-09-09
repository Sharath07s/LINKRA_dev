import pytest
import uuid
from app.db.session import SessionLocal
from app.models.resolution import CanonicalEntity
from app.ai.neo4j.intelligence import neo4j_intelligence

def test_real_data_sync_idempotency():
    """
    Test that synchronizing existing CanonicalEntities to Neo4j works and does not create duplicates.
    """
    db = SessionLocal()
    entities = db.query(CanonicalEntity).limit(4).all()
    db.close()
    
    if not entities:
        pytest.skip("No CanonicalEntity records in database.")
    
    with neo4j_intelligence.get_session() as session:
        # First pass sync
        for entity in entities:
            neo4j_intelligence.sync_canonical_entity(
                entity_id=str(entity.id),
                entity_type=entity.entity_type,
                properties={"name": entity.name}
            )
            
        # Verify count
        for entity in entities:
            count = session.run("MATCH (e:Entity {id: $id}) RETURN count(e) as c", id=str(entity.id)).single()["c"]
            assert count == 1, f"Expected 1 node for {entity.id}, got {count}"
            
        # Second pass (Idempotency check)
        for entity in entities:
            neo4j_intelligence.sync_canonical_entity(
                entity_id=str(entity.id),
                entity_type=entity.entity_type,
                properties={"name": entity.name}
            )
            
        # Verify count again
        for entity in entities:
            count = session.run("MATCH (e:Entity {id: $id}) RETURN count(e) as c", id=str(entity.id)).single()["c"]
            assert count == 1, f"Idempotency failed: Expected 1 node for {entity.id}, got {count} after second sync"
