import sys
import os
import uuid
from pathlib import Path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

from app.db.session import SessionLocal
from app.ingestion.service import process_ingestion
from app.ai.copilot.orchestrator import CopilotOrchestrator
from app.schemas.copilot import CopilotQuery

db = SessionLocal()

def run_test():
    # 1. Create a dummy txt file
    test_file_path = os.path.abspath("test_m154_doc.txt")
    with open(test_file_path, "w") as f:
        f.write("The suspect Vicky Saluja was seen near the Mysuru ATM at 23:45. He was wearing a black hoodie and drove a Honda City (KA01-HG-2345).")
        
    try:
        # 2. Ingest
        print("Starting ingestion...")
        job = process_ingestion(
            db=db,
            file_path=test_file_path,
            file_name="test_m154_doc.txt",
            file_type="txt",
            source_type="FIR",
            file_size=1024,
            user_id=None
        )
        print(f"Ingestion finished with status: {job.status}")
        
        # 3. Query Copilot Orchestrator for RAG
        print("\nQuerying Copilot...")
        query = CopilotQuery(message="What was Vicky Saluja wearing at the Mysuru ATM?")
        response = CopilotOrchestrator.handle_query(db, query, current_user=None)
        
        print(f"\nResponse Intent: {response.intent}")
        print(f"Response Answer: {response.answer}")
        print(f"Evidence chunks: {len(response.evidence)}")
        if response.evidence:
            print("First piece of evidence:", response.evidence[0])
            
    finally:
        db.close()
        if os.path.exists(test_file_path):
            os.remove(test_file_path)

if __name__ == "__main__":
    run_test()
