import asyncio
from sqlalchemy import text
from backend.app.db.session import engine

def audit_db():
    with engine.connect() as conn:
        print("=== CRIMES ===")
        try:
            total = conn.execute(text("SELECT COUNT(*) FROM crimes")).scalar()
            occ = conn.execute(text("SELECT COUNT(*) FROM crimes WHERE occurrence_date IS NOT NULL")).scalar()
            rep = conn.execute(text("SELECT COUNT(*) FROM crimes WHERE reported_date IS NOT NULL")).scalar()
            print(f"Total: {total}, With occurrence: {occ}, With reported: {rep}")
        except Exception as e:
            print(e)
            
        print("\n=== RELATIONSHIPS ===")
        try:
            total = conn.execute(text("SELECT COUNT(*) FROM entity_relationships")).scalar()
            with_ev = conn.execute(text("SELECT COUNT(*) FROM entity_relationships WHERE event_timestamp IS NOT NULL")).scalar()
            print(f"Total: {total}, With event_timestamp: {with_ev}")
        except Exception as e:
            print(e)
            
        print("\n=== COMMUNICATIONS / TRANSACTIONS / LOCATIONS ===")
        try:
            # check if there are any specific event tables
            tables = conn.execute(text("SELECT table_name FROM information_schema.tables WHERE table_schema='public'")).fetchall()
            for t in tables:
                print(f"Table: {t[0]}")
        except Exception as e:
            print(e)

if __name__ == "__main__":
    audit_db()
