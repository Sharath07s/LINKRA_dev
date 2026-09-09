import asyncio
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from backend.app.core.config import settings

def audit_gis():
    engine = create_engine(str(settings.SQLALCHEMY_DATABASE_URI))
    Session = sessionmaker(bind=engine)
    db = Session()
    try:
        res_loc = db.execute(text("SELECT count(*) FROM canonical_entities WHERE entity_type = 'LOCATION'")).scalar()
        print(f"Total Locations: {res_loc}")
        
        # Let's check how many have lat/lng in properties
        res_coords = db.execute(text("SELECT count(*) FROM canonical_entities WHERE entity_type = 'LOCATION' AND properties->>'latitude' IS NOT NULL")).scalar()
        print(f"Locations with coordinates: {res_coords}")
        
        res_crimes = db.execute(text("SELECT count(*) FROM crimes")).scalar()
        print(f"Total Crimes: {res_crimes}")
    finally:
        db.close()

if __name__ == "__main__":
    audit_gis()
