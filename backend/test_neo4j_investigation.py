from app.db.session import SessionLocal
from app.models.investigation import Investigation
from app.ai.neo4j.intelligence import neo4j_intelligence
from sqlalchemy.orm import joinedload
from sqlalchemy import select

def main():
    with SessionLocal() as db:
        inv = db.execute(select(Investigation).options(joinedload(Investigation.entities))).scalars().first()
        entity_ids = [str(e.entity_id) for e in inv.entities]
        print(f"Entities ({len(entity_ids)}):", entity_ids)

        query = """
        MATCH (n:Entity) WHERE n.id IN $entity_ids
        OPTIONAL MATCH (n)-[r]->(m:Entity) WHERE m.id IN $entity_ids
        RETURN collect(distinct n) as nodes, collect(distinct r) as edges
        """
        result = neo4j_intelligence.execute_query(query, {"entity_ids": entity_ids})
        if result and len(result) > 0:
            formatted = neo4j_intelligence._format_graph_data(result[0]["nodes"], result[0]["edges"])
            print(f"Graph: {len(formatted['nodes'])} nodes, {len(formatted['edges'])} edges")
        else:
            print("No graph data")

if __name__ == "__main__":
    main()
