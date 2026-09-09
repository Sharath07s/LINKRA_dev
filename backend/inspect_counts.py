from app.db.session import SessionLocal
from app.models.resolution import CanonicalEntity
from app.models.relationship import EntityRelationship
from app.models.entities import Suspect, Vehicle, Evidence
from app.models.investigation import Investigation
from app.models.crime import Crime
from sqlalchemy.orm import Session

db = SessionLocal()
print("CanonicalEntity count:", db.query(CanonicalEntity).count())
print("EntityRelationship count:", db.query(EntityRelationship).count())
print("Evidence count:", db.query(Evidence).count())
print("Crime count:", db.query(Crime).count())
print("Suspect count:", db.query(Suspect).count())
print("Vehicle count:", db.query(Vehicle).count())
print("Investigation count:", db.query(Investigation).count())
db.close()
