import os
import sys
import logging

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
from app.db.neo4j import neo4j_conn
from app.db.session import SessionLocal
from app.models.resolution import CanonicalEntity
from app.models.relationship import EntityRelationship
from app.models.entities import Evidence
from app.models.investigation import Investigation

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_validations():
    db = SessionLocal()
    
    print("--- M6.1 Real Data Inventory ---")
    ent_count = db.query(CanonicalEntity).count()
    rel_count = db.query(EntityRelationship).count()
    inv_count = db.query(Investigation).count()
    ev_count = db.query(Evidence).count()
    print(f"PostgreSQL CanonicalEntity count: {ent_count}")
    print(f"PostgreSQL EntityRelationship count: {rel_count}")
    print(f"PostgreSQL Investigation count: {inv_count}")
    print(f"PostgreSQL Evidence count: {ev_count}")
    
    rels = db.query(EntityRelationship).all()
    for r in rels:
        source = db.query(CanonicalEntity).get(r.source_entity_id)
        target = db.query(CanonicalEntity).get(r.target_entity_id)
        print(f"Rel: {source.name if source else 'None'} -> {target.name if target else 'None'} [{r.relationship_type}] (Conf: {r.confidence})")
        print(f"  Evidence: {r.evidence_text}")
        print(f"  Method: {r.extraction_method}")
        
    print("\n--- M6.2 & M6.4 Neo4j Inventory ---")
    try:
        with neo4j_conn.get_session() as session:
            n_count = session.run("MATCH (n:Entity) RETURN count(n)").single()[0]
            e_count = session.run("MATCH ()-[r]->() RETURN count(r)").single()[0]
            print(f"Neo4j Entity count: {n_count}")
            print(f"Neo4j Relationship count: {e_count}")
            
            edges = session.run("MATCH (a:Entity)-[r]->(b:Entity) RETURN a.id, a.name, type(r), b.id, b.name, r.evidence_text, r.extraction_method")
            for record in edges:
                print(f"Neo4j Edge: {record['a.name']} -> {record['b.name']} [{record['type(r)']}]")
                print(f"  Evidence: {record['r.evidence_text']}")
    except Exception as e:
        print(f"Neo4j Error: {e}")
            
    db.close()

if __name__ == "__main__":
    run_validations()
