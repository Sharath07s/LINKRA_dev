import sys
import os
import logging
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

from app.db.session import SessionLocal
from app.models.user import User
from app.ingestion.service import process_ingestion

def test_ingestion():
    db = SessionLocal()
    user = db.query(User).first()
    path = os.path.abspath("test_fir.txt")
    
    logger.info(f"Ingesting {path}...")
    try:
        job = process_ingestion(
            db=db,
            file_path=path,
            file_name="test_fir.txt",
            file_type="txt",
            source_type="FIR",
            file_size=os.path.getsize(path),
            user_id=user.id if user else None
        )
        logger.info(f"Successfully finished job test_fir.txt. Status: {job.status}, Entities: {job.entity_count}")
    except Exception as e:
        logger.error(f"Error ingesting test_fir.txt: {e}")

if __name__ == "__main__":
    test_ingestion()
