from app.db.session import SessionLocal
from app.models.investigation import Investigation, InvestigationEntity
from app.models.resolution import CanonicalEntity
from sqlalchemy.orm import joinedload
from sqlalchemy import select

def main():
    with SessionLocal() as db:
        result = db.execute(
            select(Investigation).options(joinedload(Investigation.entities))
        )
        invs = result.unique().scalars().all()
        print(f"Total investigations: {len(invs)}")
        for i in invs:
            print(f"Investigation {i.id} ({i.summary}): {len(i.entities)} entities")

if __name__ == "__main__":
    main()
