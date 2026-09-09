import sys
import os

# Ensure backend directory is in path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app.db.session import SessionLocal
from app.models.user import User
from app.ingestion.service import process_ingestion
from scripts.seed_database import seed_users_and_roles, seed_districts, seed_police_stations

def ingest_pdfs():
    db = SessionLocal()
    
    # Need a user
    user = db.query(User).first()
    if not user:
        print("No users in DB. Seeding users...")
        districts = seed_districts(db)
        stations = seed_police_stations(db, districts)
        users = seed_users_and_roles(db, stations)
        user = users[0]
        
    pdf_dir = "data/pdfs"
    pdfs = ["fir_2023_001.pdf", "fir_2023_045.pdf"]
    
    for pdf_name in pdfs:
        path = os.path.join(pdf_dir, pdf_name)
        if not os.path.exists(path):
            print(f"Not found: {path}")
            continue
            
        print(f"Ingesting {path}...")
        try:
            job = process_ingestion(
                db=db,
                file_path=os.path.abspath(path),
                file_name=pdf_name,
                file_type="pdf",
                source_type="FIR",
                file_size=os.path.getsize(path),
                user_id=user.id
            )
            print(f"Successfully started job {pdf_name}. Job ID: {job.id}")
        except Exception as e:
            print(f"Error ingesting {pdf_name}: {e}")

if __name__ == "__main__":
    ingest_pdfs()
