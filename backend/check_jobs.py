import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app.db.session import SessionLocal
from app.models.ingestion import IngestionJob

def check_jobs():
    db = SessionLocal()
    jobs = db.query(IngestionJob).order_by(IngestionJob.created_at.desc()).limit(5).all()
    for j in jobs:
        print(f"Job {j.id} - {j.file_name} - {j.status} - Entities: {j.entity_count}")

if __name__ == "__main__":
    check_jobs()
