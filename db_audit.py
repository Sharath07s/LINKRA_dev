import asyncio
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select, func
from backend.app.db.session import engine
from backend.app.models.crime import Crime
from backend.app.models.relationship import EntityRelationship
from backend.app.models.entities import CanonicalEntity
from backend.app.models.investigation import Investigation
from backend.app.models.ingestion import IngestionJob

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def audit_db():
    db = SessionLocal()
    
    print("=== CRIMES ===")
    crimes_total = db.query(func.count(Crime.id)).scalar()
    crimes_with_occ_date = db.query(func.count(Crime.id)).filter(Crime.occurrence_date != None).scalar()
    crimes_with_rep_date = db.query(func.count(Crime.id)).filter(Crime.reported_date != None).scalar()
    print(f"Total: {crimes_total}")
    print(f"With occurrence_date: {crimes_with_occ_date}")
    print(f"With reported_date: {crimes_with_rep_date}")
    
    print("\n=== RELATIONSHIPS ===")
    rels_total = db.query(func.count(EntityRelationship.id)).scalar()
    rels_with_event = db.query(func.count(EntityRelationship.id)).filter(EntityRelationship.event_timestamp != None).scalar()
    print(f"Total: {rels_total}")
    print(f"With event_timestamp: {rels_with_event}")
    
    print("\n=== INVESTIGATIONS ===")
    inv_total = db.query(func.count(Investigation.id)).scalar()
    inv_with_start = db.query(func.count(Investigation.id)).filter(Investigation.started_at != None).scalar()
    print(f"Total: {inv_total}")
    print(f"With started_at: {inv_with_start}")
    
    db.close()

if __name__ == "__main__":
    audit_db()
