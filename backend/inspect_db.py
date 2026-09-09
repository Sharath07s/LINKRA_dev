from app.db.session import SessionLocal
from app.models.resolution import CanonicalEntity
from app.models.relationship import EntityRelationship
from app.models.crime import Suspect, Vehicle, Crime
from sqlalchemy.orm import Session

db: Session = SessionLocal()
print("Canonical Entities:", db.query(CanonicalEntity).count())
print("Entity Relationships:", db.query(EntityRelationship).count())
print("Suspects:", db.query(Suspect).count())
print("Crimes:", db.query(Crime).count())
db.close()
