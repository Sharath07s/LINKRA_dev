import sys
import os
import logging

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.db.session import SessionLocal
from app.models.resolution import CanonicalEntity
from app.models.relationship import EntityRelationship
from app.ai.neo4j.intelligence import neo4j_intelligence

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def rebuild_graph():
    """
    Safely rebuilds the Neo4j Knowledge Graph strictly from PostgreSQL canonical data.
    This operation is idempotent.
    """
    db = SessionLocal()
    try:
        # 1. Create constraints
        logger.info("Initializing Neo4j Constraints...")
        with neo4j_intelligence.get_session() as session:
            # We want an index/constraint on Entity id
            session.run("CREATE CONSTRAINT IF NOT EXISTS FOR (e:Entity) REQUIRE e.id IS UNIQUE")
            logger.info("Constraints verified.")

        # 2. Sync Entities
        logger.info("Fetching Canonical Entities...")
        entities = db.query(CanonicalEntity).all()
        logger.info(f"Syncing {len(entities)} Canonical Entities to Neo4j...")
        
        for entity in entities:
            props = {
                "name": entity.name,
                "entity_type": entity.entity_type
            }
            if entity.attributes:
                # Merge custom attributes into props (flattened for graph indexing)
                for k, v in entity.attributes.items():
                    if isinstance(v, (str, int, float, bool)):
                        props[k] = v
                        
            neo4j_intelligence.sync_canonical_entity(
                entity_id=str(entity.id),
                entity_type=entity.entity_type,
                properties=props
            )
            
        logger.info("Entity sync completed.")

        # 3. Sync Relationships
        logger.info("Fetching Entity Relationships...")
        relationships = db.query(EntityRelationship).all()
        logger.info(f"Syncing {len(relationships)} Entity Relationships to Neo4j...")
        
        for rel in relationships:
            props = {
                "confidence": rel.confidence,
                "extraction_method": rel.extraction_method,
                "status": rel.status,
                "event_timestamp": rel.event_timestamp.isoformat() if rel.event_timestamp else None,
                "source_page": rel.source_page,
                "source_row": rel.source_row,
                "ingestion_job_id": str(rel.ingestion_job_id) if rel.ingestion_job_id else None,
            }
            
            neo4j_intelligence.sync_relationship(
                relationship_id=str(rel.id),
                source_id=str(rel.source_entity_id),
                target_id=str(rel.target_entity_id),
                relationship_type=rel.relationship_type,
                properties=props
            )
            
        logger.info("Relationship sync completed.")
        logger.info("Graph Rebuild SUCCESSFUL.")
        
    except Exception as e:
        logger.error(f"Failed to rebuild graph: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    rebuild_graph()
