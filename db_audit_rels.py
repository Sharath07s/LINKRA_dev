import asyncio
from sqlalchemy import text
from backend.app.db.session import engine

def audit_db():
    with engine.connect() as conn:
        print("\n=== RELATIONSHIP TYPES ===")
        try:
            res = conn.execute(text("SELECT relationship_type, COUNT(*) FROM entity_relationships GROUP BY relationship_type")).fetchall()
            for r in res:
                print(f"{r[0]}: {r[1]}")
        except Exception as e:
            print(e)
            
        print("\n=== CANONICAL ENTITIES ===")
        try:
            total = conn.execute(text("SELECT COUNT(*) FROM canonical_entities")).scalar()
            print(f"Total entities: {total}")
            res = conn.execute(text("SELECT entity_type, COUNT(*) FROM canonical_entities GROUP BY entity_type")).fetchall()
            for r in res:
                print(f"{r[0]}: {r[1]}")
        except Exception as e:
            print(e)

if __name__ == "__main__":
    audit_db()
