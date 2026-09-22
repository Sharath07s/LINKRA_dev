import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))
from app.db.session import SessionLocal
from sqlalchemy import text

db = SessionLocal()
try:
    db.execute(text("UPDATE alembic_version SET version_num = '1fb69dab13ab'"))
    db.commit()
    print("Fixed alembic_version")
except Exception as e:
    print(f"Error: {e}")
    db.rollback()
finally:
    db.close()
