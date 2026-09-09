from app.db.session import SessionLocal
from app.models.ingestion import IngestionJob, EntityCandidate
from app.models.resolution import CanonicalEntity

db = SessionLocal()
jobs = db.query(IngestionJob).count()
candidates = db.query(EntityCandidate).count()
entities = db.query(CanonicalEntity).count()

print(f"Jobs: {jobs}")
print(f"Candidates: {candidates}")
print(f"Entities: {entities}")
